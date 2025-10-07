import asyncio
import logging
import os
import pytz
from datetime import datetime
from typing import Dict, Optional
import sys
import discord
from discord import PartialMessageable
from discord.ext import commands

from utils.utils import DiscordHandler
from utils.async_translator import AsyncDeepTranslator


class DClient(commands.Bot):
    def __init__(self, intents: discord.Intents, prefix: str, test: bool):
        super().__init__(command_prefix= prefix, intents=intents)


        self.test = test

        self.loaded_persistent_views: bool = False

        # Safely parse log channel ID; create a messageable only if valid
        log_channel_raw = os.getenv('LOG_CHANNEL', '')
        try:
            log_channel_id = int(log_channel_raw) if str(log_channel_raw).strip() else 0
        except ValueError:
            log_channel_id = 0
        self.dLogChannel: Optional[PartialMessageable] = (
            PartialMessageable(self._connection, log_channel_id) if log_channel_id > 0 else None
        )

        self.translator = AsyncDeepTranslator(timeout=30)  # 30 second timeout
        self.scheduled_post_tasks: Dict[int, asyncio.Task] = {}

    async def setup_hook(self):
        # Sync slash commands
        # Accept either a comma-separated SYNC_GUILD_IDS or a single GUILD_ID
        sync_ids_raw = os.getenv('SYNC_GUILD_IDS', '').strip()
        single_guild_raw = os.getenv('GUILD_ID', '').strip()
        if not sync_ids_raw and single_guild_raw:
            sync_ids_raw = single_guild_raw

        if sync_ids_raw:
            guild_ids = [int(x) for x in sync_ids_raw.split(',') if x.strip().isdigit()]
            for gid in guild_ids:
                try:
                    await self.tree.sync(guild=discord.Object(id=gid))
                    logging.info(f'Slash commands synced to guild {gid}')
                except Exception as e:
                    logging.error(f'Failed to sync commands to guild {gid}: {e}')
        else:
            synced = await self.tree.sync()
            logging.info(f'Slash commands globally synced: {len(synced)} commands')

        logging.info(f'We have logged in as {self.user}')

        self.translator = AsyncDeepTranslator(timeout=30)  # 30 second timeout
        
        # print "ready" in the console when the bot is ready to work
        #loads all extensions
        if not self.test:
            for extension in os.listdir('./Cogs'):
                if extension.endswith('.py'):
                    try:
                        await self.load_extension(f'Cogs.{extension[:-3]}')
                        logging.info(f'loaded {extension}')
                    except Exception as e:
                        logging.critical(f"Failed to load extension {extension}.")
                        logging.error(e)
        else:
            await self.load_extension(f'Cogs.debug')
        
        logging.info("ready")

    async def close(self): # put bot cleanup code here
        await super().close()
        discord_handlers = [handler for handler in logging.getLogger().handlers if isinstance(handler, DiscordHandler)]
        if discord_handlers:
            try:
                discord_handlers[0].close()
            except Exception:
                pass
 
    @staticmethod
    async def error(channel: discord.abc.Messageable, message: str):
        return await channel.send(embed=discord.Embed(title="Error", description=message, color=discord.Color.red()))
    
    async def on_command_error(self, ctx: commands.Context, error) -> None:
        logging.error(error)
        embed = discord.Embed(
            title= 'Error', description= f'Something Went Wrong, try ;help ({error})', color=discord.Color.red(), timestamp= datetime.utcnow()
        )
        await ctx.send(embed= embed)
