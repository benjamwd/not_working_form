import logging
from discord.ext import commands


class Debug(commands.Cog):
    """Debug commands for testing"""
    
    def __init__(self, bot):
        self.bot = bot
        logging.info('Debug cog loaded')

    @commands.command(name='ping')
    async def ping(self, ctx):
        """Simple ping command for testing"""
        await ctx.send('Pong!')


async def setup(bot):
    await bot.add_cog(Debug(bot))

