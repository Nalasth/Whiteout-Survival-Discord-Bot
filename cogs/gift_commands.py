import discord
from discord.ext import commands

class GiftCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="gift")
    async def gift(self, ctx):
        """Commande de test pour les gifts"""
        await ctx.send("🎁 Gift command works!")

# Fonction setup obligatoire pour charger le cog
async def setup(bot):
    await bot.add_cog(GiftCommands(bot))
