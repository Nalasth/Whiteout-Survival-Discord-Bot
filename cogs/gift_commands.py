import sqlite3
from discord.ext import commands

class GiftCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="gift")
    async def gift(self, ctx):
        discord_id = ctx.author.id
        conn = sqlite3.connect("db/users.sqlite")
        cursor = conn.cursor()
        cursor.execute("SELECT nickname, role FROM users WHERE discord_id=?", (discord_id,))
        user = cursor.fetchone()
        conn.close()

        if user:
            nickname, role = user
            await ctx.send(f"Salut {nickname} ! Ton rôle est {role}. Voici ton cadeau ! 🎁")
        else:
            await ctx.send("Utilisateur non trouvé dans la base de données.")

def setup(bot):
import sqlite3
from discord.ext import commands

class GiftCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="gift")
    async def gift(self, ctx):
        discord_id = ctx.author.id
        conn = sqlite3.connect("db/users.sqlite")
        cursor = conn.cursor()
        cursor.execute("SELECT nickname, role FROM users WHERE discord_id=?", (discord_id,))
        user = cursor.fetchone()
        conn.close()

        if user:
            nickname, role = user
            await ctx.send(f"Salut {nickname} ! Ton rôle est {role}. Voici ton cadeau ! 🎁")
        else:
            await ctx.send("Utilisateur non trouvé dans la base de données.")

def setup(bot):
    bot.add_cog(GiftCommands(bot))

import sqlite3
from discord.ext import commands

class GiftCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="gift")
    async def gift(self, ctx):
        discord_id = ctx.author.id
        conn = sqlite3.connect("db/users.sqlite")
        cursor = conn.cursor()
        cursor.execute("SELECT nickname, role FROM users WHERE discord_id=?", (discord_id,))
        user = cursor.fetchone()
        conn.close()

        if user:
            nickname, role = user
            await ctx.send(f"Salut {nickname} ! Ton rôle est {role}. Voici ton cadeau ! 🎁")
        else:
            await ctx.send("Utilisateur non trouvé dans la base de données.")

def setup(bot):
    bot.add_cog(GiftCommands(bot))

import sqlite3
from discord.ext import commands

class GiftCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="gift")
    async def gift(self, ctx):
        discord_id = ctx.author.id
        conn = sqlite3.connect("db/users.sqlite")
        cursor = conn.cursor()
        cursor.execute("SELECT nickname, role FROM users WHERE discord_id=?", (discord_id,))
        user = cursor.fetchone()
        conn.close()

        if user:
            nickname, role = user
            await ctx.send(f"Salut {nickname} ! Ton rôle est {role}. Voici ton cadeau ! 🎁")
        else:
            await ctx.send("Utilisateur non trouvé dans la base de données.")

def setup(bot):
    bot.add_cog(GiftCommands(bot))
import sqlite3
from discord.ext import commands

class GiftCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="gift")
    async def gift(self, ctx):
        discord_id = ctx.author.id
        conn = sqlite3.connect("db/users.sqlite")
        cursor = conn.cursor()
        cursor.execute("SELECT nickname, role FROM users WHERE discord_id=?", (discord_id,))
        user = cursor.fetchone()
        conn.close()

        if user:
            nickname, role = user
            await ctx.send(f"Salut {nickname} ! Ton rôle est {role}. Voici ton cadeau ! 🎁")
        else:
            await ctx.send("Utilisateur non trouvé dans la base de données.")

def seimport sqlite3
from discord.ext import commands

class GiftCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="gift")
    async def gift(self, ctx):
        discord_id = ctx.author.id
        conn = sqlite3.connect("db/users.sqlite")
        cursor = conn.cursor()
        cursor.execute("SELECT nickname, role FROM users WHERE discord_id=?", (discord_id,))
        user = cursor.fetchone()
        conn.close()

        if user:
            nickname, role = user
            await ctx.send(f"Salut {nickname} ! Ton rôle est {role}. Voici ton cadeau ! 🎁")
        else:
            await ctx.send("Utilisateur non trouvé dans la base de données.")

def setup(bot):
phyton
import sqlite3
from discord.ext import commands

class GiftCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="gift")
    async def gift(self, ctx):
        discord_id = ctx.author.id
        conn = sqlite3.connect("db/users.sqlite")
        cursor = conn.cursor()
        cursor.execute("SELECT nickname, role FROM users WHERE discord_id=?", (discord_id,))
        user = cursor.fetchone()
        conn.close()

        if user:
            nickname, role = user
            await ctx.send(f"Salut {nickname} ! Ton rôle est {role}. Voici ton cadeau ! 🎁")
        else:
            await ctx.send("Utilisateur non trouvé dans la base de données.")

def setup(bot):
    bot.add_cog(GiftCommands(bot))
phyton
import sqlite3
from discord.ext import commands

class GiftCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="gift")
    async def gift(self, ctx):
        discord_id = ctx.author.id
        conn = sqlite3.connect("db/users.sqlite")
        cursor = conn.cursor()
        cursor.execute("SELECT nickname, role FROM users WHERE discord_id=?", (discord_id,))
        user = cursor.fetchone()
        conn.close()

        if user:
            nickname, role = user
            await ctx.send(f"Salut {nickname} ! Ton rôle est {role}. Voici ton cadeau ! 🎁")
        else:
            await ctx.send("Utilisateur non trouvé dans la base de données.")

def setup(bot):
import sqlite3
from discord.ext import commands

class GiftCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="gift")
    async def gift(self, ctx):
        discord_id = ctx.author.id
        conn = sqlite3.connect("db/users.sqlite")
        cursor = conn.cursor()
        cursor.execute("SELECT nickname, role FROM users WHERE discord_id=?", (discord_id,))
        user = cursor.fetchone()
        conn.close()

        if user:
            nickname, role = user
            await ctx.send(f"Salut {nickname} ! Ton rôle est {role}. Voici ton cadeau ! 🎁")
        else:
            await ctx.send("Utilisateur non trouvé dans la base de données.")

def setup(bot):
    bot.add_cog(GiftCommands(bot))
import sqlite3
from discord.ext import commands

class GiftCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="gift")
    async def gift(self, ctx):
        discord_id = ctx.author.id
        conn = sqlite3.connect("db/users.sqlite")
        cursor = conn.cursor()
        cursor.execute("SELECT nickname, role FROM users WHERE discord_id=?", (discord_id,))
        user = cursor.fetchone()
        conn.close()

        if user:
            nickname, role = user
            await ctx.send(f"Salut {nickname} ! Ton rôle est {role}. Voici ton cadeau ! 🎁")
        else:
            await ctx.send("Utilisateur non trouvé dans la base de données.")

def setup(bot):
    bot.add_cog(GiftCommands(bot))

phytonimport sqlite3
from discord.ext import commands

class GiftCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="gift")
    async def gift(self, ctx):
        discord_id = ctx.author.id
        conn = sqlite3.connect("db/users.sqlite")
        cursor = conn.cursor()
        cursor.execute("SELECT nickname, role FROM users WHERE discord_id=?", (discord_id,))
        user = cursor.fetchone()
        conn.close()

        if user:
            nickname, role = user
            await ctx.send(f"Salut {nickname} ! Ton rôle est {role}. Voici ton cadeau ! 🎁")
        else:
            await ctx.send("Utilisateur non trouvé dans la base de données.")

def setup(bot):
    bot.add_cog(GiftCommands(bot))

