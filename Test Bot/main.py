import logging
import os
from logging.handlers import TimedRotatingFileHandler

import discord
import dotenv

from utils.bot import DClient
from utils.utils import DiscordHandler

dotenv.load_dotenv(override=True)
dToken = os.getenv('DISCORD_TOKEN')
lToken = os.getenv('LANGUAGE_TOKEN')
log_level = os.getenv('LOG_LEVEL', logging.INFO)
webhook_url = os.getenv('WEBHOOK_URL')

test = os.getenv("TEST", "").lower() == 'true' # TODO make this a flag in the start command

prefix = ';'

if test:
    log_level = logging.DEBUG

#TODO setup log level definition, probably worthwhile to set it up as a start command arg

intents = discord.Intents.all() 
intents.message_content = True

discord.utils.setup_logging(level=log_level, root=True)
if not os.path.exists('./Logs'):
    os.mkdir('./Logs')
file_handler = TimedRotatingFileHandler('./Logs/BNN-Translator.log', when='midnight', backupCount=10)
file_handler.suffix = "%Y-%m-%d"
file_handler.setFormatter(logging.Formatter(' [{asctime}] [{levelname:<8}] {name}: {message}', '%Y-%m-%d %H:%M:%S', style='{'))
file_handler.setLevel(logging.DEBUG)  # Write DEBUG logs (or higher) to a file

discord_handler = DiscordHandler(webhook_url)
discord_handler.setLevel(logging.ERROR)
root_logger = logging.getLogger()
root_logger.addHandler(discord_handler)
root_logger.addHandler(file_handler)


dClient = DClient(intents, prefix, test)

dClient.run(dToken, log_handler=None)

