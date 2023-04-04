"""Filter chat messages"""
import logging
_LOG = logging.getLogger(__name__)

import discord
import doosbot.client

def init(client: doosbot.client.DoosBotClient, tree: discord.app_commands.CommandTree):
	
	@client.event
	async def on_message(message: discord.message.Message):
		_LOG.info(f"MESSAGE { message.author.display_name }: { message.content }")
		try:

			if("kom" in message.content and not "soep" in message.content):
				_LOG.info(f"KOM SOEP module triggered by { message.author.name }")
				for character in "SOEP":
					emoji_character = chr(ord(character) + ord("🇦") - ord("A"))
					await message.add_reaction(emoji_character)

		except Exception as e:
			_LOG.error(f"Error handling chat message: { e }")
			try:
				await message.reply(f"Oeps, DoosBot went full-krak: `{ e }`")
			except:
				_LOG.error(f"Error while sending the error report to the channel")