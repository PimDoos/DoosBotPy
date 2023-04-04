import logging
_LOG = logging.getLogger(__name__)

import discord
import doosbot.client
import doosbot.modules.chat
import doosbot.modules.dice
import doosbot.modules.lingo
import doosbot.modules.voice
import doosbot.modules.wikipedia
import doosbot.modules.youtube


def init(client: doosbot.client.DoosBotClient):
	tree = discord.app_commands.CommandTree(client)

	@client.event
	async def on_ready():
		await tree.sync()
		
	doosbot.modules.chat.init(client, tree)	
	doosbot.modules.dice.init(client, tree)
	doosbot.modules.lingo.init(client, tree)
	doosbot.modules.voice.init(client, tree)
	doosbot.modules.wikipedia.init(client, tree)
	doosbot.modules.youtube.init(client, tree)
	