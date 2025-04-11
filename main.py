print("[DoosBot Startup] Loading dependencies...", end="", flush=True)
import discord
import logging

import doosbot.modules

from doosbot.client import DoosBotClient
from doosbot.utils import setup_logging
from config import DISCORD_SECRET
print(" [ DONE ]")

setup_logging()
_LOG = logging.getLogger(__name__)

_LOG.info("Loading Discord Client...")
intents = discord.Intents.default()
intents.message_content = True

client = DoosBotClient(command_prefix="",intents=intents)

_LOG.info("Loading DoosBot Modules...")
doosbot.modules.init(client)

_LOG.info("Starting DoosBot client")
client.run(token=DISCORD_SECRET)

_LOG.info("DoosBot exited")