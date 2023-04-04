

import logging
import sys
import discord.utils

_LOG = logging.getLogger(__name__)

def setup_logging():

	log_handler = logging.StreamHandler(sys.stdout)
	log_handler.setLevel(logging.INFO)
	log_formatter = discord.utils._ColourFormatter()
	log_handler.setFormatter(log_formatter)

	discord.utils.setup_logging(handler=log_handler,formatter=log_formatter)

