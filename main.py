import sys
import discord
import logging

import doosbot.modules

from doosbot.client import DoosBotClient
from doosbot.utils import setup_logging
from config import DISCORD_SECRET

setup_logging()

intents = discord.Intents.default()
intents.message_content = True

client = DoosBotClient(intents=intents)
doosbot.modules.init(client)


client.run(token=DISCORD_SECRET)