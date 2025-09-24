import os
import json
import aiohttp
import asyncio
import sqlite3
import re
from datetime import datetime
import traceback
import discord
import ssl
from typing import List, Tuple, Optional


APP_DB_PATH = "db/app.sqlite"          # <- base unique
OLD_DB_GIFTCODE = "db/giftcode.sqlite" # <- anciennes bases (migration auto)
OLD_DB_SETTINGS = "db/settings.sqlite"
OLD_DB_USERS = "db/users.sqlite"


class GiftCodeAPI:
    """
    Service de synchro des gift codes avec l'API distante + gestion DB + notifications.
    Centralise toutes les tables dans une seule base db/app.sqlite.
    """

    def __init__(self, bot):
        self.bot = bot
        self.api_url = "https://wosland.com/apidc/giftapi/giftcode_api.php"
        self.api_key = "serioyun_gift_api_key_2024"
        self.check_interval = 300  # secondes

        # 1) Connexion unique SQLite (partageable avec bot.conn si déjà fourni)
        if hasattr(bot, 'conn') and isinstance(bot.conn, sqlite3.Connection):
            self.conn = bot.conn
        else:
            os.makedirs("db", exist_ok=True)
            self.conn = sqlite3.connect(APP_DB_PATH, check_same_thread=False)
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self.cursor = self.conn.cursor()

        # 2) Prépare le schéma (création si manquant)
        self._ensure_schema()

        # 3) Migration auto depuis anciennes bases si présentes
        #    (s’exécute une fois — idempotent grâce aux INSERT OR IGNORE)
        try:
            self._maybe_migrate_from_old_dbs()
        except Exception:
            traceback.print_exc()

        # 4) SSL permissif (si l’API a un cert bancal)
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE

        # 5) Lance la tâche de fond
        asyncio.create_task(self.start_api_check())

    # ---------- Schéma centralisé ----------
    def _ensure_schema(self):
        """
        Crée les tables nécessaires si elles n’existent pas déjà.
        Adapte les noms/colonnes aux usages de ton bot.
        """
        # Codes disponibles
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS gift_codes (
                giftcode TEXT PRIMARY KEY,
                date TEXT NOT NULL
            );
        """)

        # Liens user<->codes (si ton bot l’utilise)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_giftcodes (
                user_id TEXT NOT NULL,
                giftcode TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                PRIMARY KEY (user_id, giftcode),
                FOREIGN KEY (giftcode) REFERENCES gift_codes(giftcode) ON DELETE CASCADE
            );
        """)

        # Contrôle auto-claim par alliance
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS giftcodecontrol (
                alliance_id TEXT PRIMARY KEY,
                status INTEGER NOT NULL DEFAULT 0
            );
        """)

        # Admins (ex- settings.admin)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin (
                id TEXT PRIMARY KEY,
                is_initial INTEGER NOT NULL DEFAULT 0
            );
        """)

        # (Optionnel) Table users si nécessaire pour d’autres features
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                name TEXT
            );
        """)

        self.conn.commit()

    def _maybe_migrate_from_old_dbs(self):
        """
        Migre les données depuis les anciennes bases si elles existent.
        Cette migration est simple et idempotente (INSERT OR IGNORE).
        Tu peux supprimer cette méthode quand tu n’as plus besoin de migrer.
        """
        # Migration gift_codes + user_giftcodes + giftcodecontrol (depuis giftcode.sqlite)
        if os.path.exists(OLD_DB_GIFTCODE):
            try:
                old = sqlite3.connect(OLD_DB_GIFTCODE, check_same_thread=False)
                old_cur = old.cursor()
                # gift_codes
                try:
                    for giftcode, date_str in old_cur.execute("SELECT giftcode, date FROM gift_codes"):
                        self.cursor.execute(
                            "INSERT OR IGNORE INTO gift_codes (giftcode, date) VALUES (?, ?)",
                            (giftcode, date_str)
                        )
                except Exception:
                    pass
                # user_giftcodes
                try:
                    for user_id, giftcode in old_cur.execute("SELECT user_id, giftcode FROM user_giftcodes"):
                        self.cursor.execute(
                            "INSERT OR IGNORE INTO user_giftcodes (user_id, giftcode) VALUES (?, ?)",
                            (str(user_id), giftcode)
                        )
                except Exception:
                    pass
                # giftcodecontrol
                try:
                    for alliance_id, status in old_cur.execute("SELECT alliance_id, status FROM giftcodecontrol"):
                        self.cursor.execute(
                            "INSERT OR IGNORE INTO giftcodecontrol (alliance_id, status) VALUES (?, ?)",
                            (str(alliance_id), int(status or 0))
                        )
                except Exception:
                    pass
                old.close()
            except Exception:
                traceback.print_exc()

        # Migration admin (depuis settings.sqlite)
        if os.path.exists(OLD_DB_SETTINGS):
            try:
                old = sqlite3.connect(OLD_DB_SETTINGS, check_same_thread=False)
                old_cur = old.cursor()
                try:
                    for (admin_id, is_initial) in old_cur.execute("SELECT id, is_initial FROM admin"):
                        self.cursor.execute(
                            "INSERT OR IGNORE INTO admin (id, is_initial) VALUES (?, ?)",
                            (str(admin_id), int(is_initial or 0))
                        )
                except Exception:
                    pass
                old.close()
            except Exception:
                traceback.print_exc()

        # Migration users (depuis users.sqlite) — optionnel
        if os.path.exists(OLD_DB_USERS):
            try:
                old = sqlite3.connect(OLD_DB_USERS, check_same_thread=False)
                old_cur = old.cursor()
                try:
                    # Adapte si ton schéma users diffère
                    for (uid,) in old_cur.execute("SELECT id FROM users"):
                        self.cursor.execute(
                            "INSERT OR IGNORE INTO users (id) VALUES (?)",
                            (str(uid),)
                        )
                except Exception:
                    pass
                old.close()
            except Exception:
                traceback.print_exc()

        self.conn.commit()

    # ---------- Boucle de synchro ----------
    async def start_api_check(self):
        """Démarre la boucle de synchro périodique."""
        try:
            await asyncio.sleep(60)  # Laisse le bot démarrer
            await self.sync_with_api()

            while True:
                await asyncio.sleep(self.check_interval)
                await self.sync_with_api()
        except Exception:
            traceback.print_exc()

    def __del__(self):
        try:
            # Si c’est bot.conn, on ne ferme pas ici.
            if not (hasattr(self.bot, 'conn') and self.conn is self.bot.conn):
                try:
                    self.conn.close()
                except Exception:
                    pass
        except Exception:
            pass

    # ---------- Logique API ----------
    async def sync_with_api(self) -> Optional[bool]:
        """
        - Lit les codes depuis l’API
        - Valide / nettoie les lignes invalides (DELETE côté API)
        - Insère les nouveaux codes en DB
        - Notifie les admins
        - Auto-claim pour les alliances avec status=1
        - Up-sync : pousse nos codes DB vers l’API
        """
        try:
            # 1) Codes déjà en DB
            self.cursor.execute("SELECT giftcode, date FROM gift_codes")
            db_codes = {row[0]: row[1] for row in self.cursor.fetchall()}

            connector = aiohttp.TCPConnector(ssl=self.ssl_context)
            headers = {'X-API-Key': self.api_key, 'Content-Type': 'application/json'}

            # 2) GET API
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(self.api_url, headers=headers) as response:
                    response_text = await response.text()
                    status = response.status

            if status != 200:
                print(f"⚠️ API HTTP {status} – corps: {response_text[:200]}")
                return None

            if not response_text.strip():
                print("⚠️ API a retourné une réponse vide")
                return None

            try:
                result = json.loads(response_text)
            except json.JSONDecodeError as e:
                print(f"⚠️ Erreur JSON: {e} | Réponse: {response_text[:200]}")
                return None

            if isinstance(result, dict) and 'error' in result:
                print(f"⚠️ Erreur API: {result.get('error')}")
                return False

            # 3) Parsing
            api_giftcodes = result.get('codes', []) if isinstance(result, dict) else []
            valid_codes: List[Tuple[str, datetime]] = []
            invalid_codes: List[str] = []

            for code_line in api_giftcodes:
                line = (code_line or "").strip()
                parts = line.split()
                if len(parts) != 2:
                    invalid_codes.append(line)
                    continue

                code, date_str = parts
                if not re.match(r"^[a-zA-Z0-9]+$", code):
                    invalid_codes.append(line)
                    continue

                try:
                    date_obj = datetime.strptime(date_str, "%d.%m.%Y")
                    valid_codes.append((code, date_obj))
                except ValueError:
                    invalid_codes.append(line)

            # 4) Nettoyage côté API
            if invalid_codes:
                async with aiohttp.ClientSession(connector=connector) as session:
                    for invalid_line in invalid_codes:
                        try:
                            code = invalid_line.split()[0] if ' ' in invalid_line else invalid_line
                            await session.delete(self.api_url, json={'code': code}, headers=headers)
                            await asyncio.sleep(0.25)
                        except Exception:
                            traceback.print_exc()

            # 5) Insert nouveaux codes en DB
            new_codes: List[Tuple[str, str]] = []
            for code, date_obj in valid_codes:
                formatted_date = date_obj.strftime("%Y-%m-%d")
                if code not in db_codes:
                    try:
                        self.cursor.execute(
                            "INSERT OR IGNORE INTO gift_codes (giftcode, date) VALUES (?, ?)",
                            (code, formatted_date)
                        )
                        new_codes.append((code, formatted_date))
                    except Exception:
                        traceback.print_exc()

            try:
                self.conn.commit()
            except Exception:
                traceback.print_exc()

            # 6) Notifications + Auto-claim
            if new_codes:
                try:
                    # Alliances en auto (status=1)
                    self.cursor.execute("SELECT alliance_id FROM giftcodecontrol WHERE status = 1")
                    auto_alliances = self.cursor.fetchall() or []

                    # Admins
                    self.cursor.execute("SELECT id FROM admin WHERE is_initial = 1")
                    admin_ids = self.cursor.fetchall() or []

                    # DM aux admins
                    if admin_ids:
                        now_ts = int(datetime.now().timestamp())
                        for code, formatted_date in new_codes:
                            embed = discord.Embed(
                                title="🎁 New Gift Code Found!",
                                description=(
                                    f"**Gift Code Details**\n"
                                    f"━━━━━━━━━━━━━━━━━━━━━━\n"
                                    f"🎁 **Code:** `{code}`\n"
                                    f"📅 **Date:** `{formatted_date}`\n"
                                    f"📝 **Status:** `Retrieved from Reloisback API`\n"
                                    f"⏰ **Time:** <t:{now_ts}:R>\n"
                                    f"🔄 **Auto Alliance Count:** `{len(auto_alliances)}`\n"
                                    f"━━━━━━━━━━━━━━━━━━━━━━\n"
                                ),
                                color=discord.Color.green()
                            )
                            for (admin_id,) in admin_ids:
                                try:
                                    admin_user = await self.bot.fetch_user(int(admin_id))
                                    if admin_user is not None:
                                        await admin_user.send(embed=embed)
                                except discord.Forbidden:
                                    pass
                                except Exception:
                                    traceback.print_exc()

                    # Auto-claim
                    if auto_alliances:
                        gift_operations = self.bot.get_cog('GiftOperations')
                        if gift_operations and hasattr(gift_operations, 'use_giftcode_for_alliance'):
                            for (alliance_id,) in auto_alliances:
                                for code, _d in new_codes:
                                    try:
                                        await gift_operations.use_giftcode_for_alliance(str(alliance_id), code)
                                        await asyncio.sleep(1)
                                    except Exception:
                                        traceback.print_exc()
                        else:
                            print("⚠️ Cog GiftOperations introuvable ou méthode absente pour auto-claim.")

                except Exception:
                    traceback.print_exc()

            # 7) Up-sync nos codes vers l’API
            if db_codes:
                async with aiohttp.ClientSession(connector=connector) as session:
                    for db_code, db_date in db_codes.items():
                        try:
                            date_obj = datetime.strptime(db_date, "%Y-%m-%d")
                            formatted_date = date_obj.strftime("%d.%m.%Y")
                            await session.post(self.api_url, json={'code': db_code, 'date': formatted_date}, headers=headers)
                            await asyncio.sleep(0.05)
                        except Exception:
                            traceback.print_exc()

            return True

        except Exception:
            traceback.print_exc()
            return None

    # ---------- Helpers publics ----------
    async def add_giftcode(self, giftcode: str) -> bool:
        """Ajoute un giftcode (local + API)."""
        try:
            self.cursor.execute("SELECT 1 FROM gift_codes WHERE giftcode = ?", (giftcode,))
            if self.cursor.fetchone():
                return False

            connector = aiohttp.TCPConnector(ssl=self.ssl_context)
            headers = {'Content-Type': 'application/json', 'X-API-Key': self.api_key}
            date_str_api = datetime.now().strftime("%d.%m.%Y")
            payload = {'code': giftcode, 'date': date_str_api}

            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.post(self.api_url, json=payload, headers=headers) as response:
                    if response.status != 200:
                        return False
                    try:
                        result = await response.json()
                    except Exception:
                        result = {}

            if result.get('success', True):
                self.cursor.execute(
                    "INSERT OR IGNORE INTO gift_codes (giftcode, date) VALUES (?, ?)",
                    (giftcode, datetime.now().strftime("%Y-%m-%d"))
                )
                self.conn.commit()
                return True

            return False

        except Exception:
            traceback.print_exc()
            try:
                self.conn.rollback()
            except Exception:
                pass
            return False

    async def remove_giftcode(self, giftcode: str, from_validation: bool = False) -> bool:
        """
        Supprime un giftcode localement et côté API (seulement si from_validation=True
        pour éviter les suppressions indésirables).
        """
        try:
            if not from_validation:
                return False

            connector = aiohttp.TCPConnector(ssl=self.ssl_context)
            headers = {'Content-Type': 'application/json', 'X-API-Key': self.api_key}

            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.delete(self.api_url, json={'code': giftcode}, headers=headers) as response:
                    body = await response.text()
                    if response.status != 200:
                        return False
                    try:
                        result = json.loads(body)
                    except json.JSONDecodeError:
                        return False

            success = bool(result.get('success', False) or ('success' in result))
            if not success:
                return False

            try:
                self.cursor.execute("DELETE FROM user_giftcodes WHERE giftcode = ?", (giftcode,))
                self.cursor.execute("DELETE FROM gift_codes WHERE giftcode = ?", (giftcode,))
                self.conn.commit()
                return True
            except Exception:
                traceback.print_exc()
                try:
                    self.conn.rollback()
                except Exception:
                    pass
                return False

        except Exception:
            traceback.print_exc()
            return False

    async def check_giftcode(self, giftcode: str) -> bool:
        """Vérifie l’existence d’un giftcode côté API (si l’endpoint le supporte)."""
        try:
            connector = aiohttp.TCPConnector(ssl=self.ssl_context)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(f"{self.api_url}?action=check&giftcode={giftcode}") as response:
                    if response.status != 200:
                        return False
                    try:
                        result = await response.json()
                    except Exception:
                        return False
                    return bool(result.get('exists', False))
        except Exception:
            traceback.print_exc()
            return False

    async def validate_and_clean_giftcode_file(self):
        """
        Parcourt les codes en DB, essaye de claim via GiftOperations.claim_giftcode_rewards_wos,
        et supprime ceux invalides/expirés/limités côté API + DB.
        """
        try:
            self.cursor.execute("SELECT giftcode FROM gift_codes")
            rows = self.cursor.fetchall()
            if not rows:
                return

            gift_ops = self.bot.get_cog('GiftOperations')
            if not gift_ops or not hasattr(gift_ops, 'claim_giftcode_rewards_wos'):
                print("⚠️ Cog GiftOperations introuvable ou méthode 'claim_giftcode_rewards_wos' absente.")
                return

            for (code,) in rows:
                try:
                    status = await gift_ops.claim_giftcode_rewards_wos("244886619", code)
                except Exception:
                    traceback.print_exc()
                    status = None

                if status in {"TIME_ERROR", "CDK_NOT_FOUND", "USAGE_LIMIT"}:
                    await self.remove_giftcode(code, from_validation=True)

                await asyncio.sleep(1)

        except Exception:
            traceback.print_exc()
