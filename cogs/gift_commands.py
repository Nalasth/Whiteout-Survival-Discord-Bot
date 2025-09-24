import discord
from discord.ext import commands

class GiftCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="gift")
    async def gift(self, ctx: commands.Context):
        """Ping de test pour vérifier que le cog charge bien."""
        await ctx.send("🎁 Gift command works!")

async def setup(bot: commands.Bot):
    await bot.add_cog(GiftCommands(bot))
