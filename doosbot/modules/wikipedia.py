"""Read articles from wikipedia"""
import logging
_LOG = logging.getLogger(__name__)

import discord
import doosbot.client
from doosbot.const import *

import aiohttp
import re
import urllib.parse

def init(client: doosbot.client.DoosBotClient, tree: discord.app_commands.CommandTree):

	@client.listen('on_message')
	async def on_message(message: discord.message.Message):
		if(message.type == discord.MessageType.reply and message.reference != None and message.reference.cached_message != None):
			if(re.match("wat", message.content.lower())):
				response = await handle_question(message, message.author)
				if response is None:
					await message.reply("Wat moet ik daar nou mee?")
				else:
					await message.reply(response)

	@client.listen('on_reaction_add')
	async def on_reaction_add(reaction: discord.Reaction, user: discord.User):
		if reaction.emoji == DoosBotEmoji.QUESTION:
			response = await handle_question(reaction, user)
			if response is None:
				await reaction.message.channel.send(f"{ user.mention } Wat moet ik daar nou mee?")
			else:
				await reaction.message.channel.send(f"{ user.mention } { response }")

	@tree.context_menu(name="wiki")
	async def context_menu_get_article(interaction: discord.Interaction, message: discord.Message):
		"""Context menu command to search for a wiki article"""
		_LOG.info(f"{ interaction.command.name } command executed by { interaction.user.name }")
		response = await handle_question(message, interaction.user)
		if response is None:
			await interaction.response.send_message(f"Wat moet ik daar nou mee?")
		else:
			await interaction.response.send_message(response)


	@tree.command(name="wiki", description = "Zoek op Wikipedia")
	async def command_get_article(interaction: discord.Interaction, query: str):
		_LOG.info(f"{ interaction.command.name } command executed by { interaction.user.name }")
		response = await handle_question(interaction, interaction.user)
		if response is None:
			await interaction.response.send_message(f"Wat moet ik daar nou mee?")
		else:
			await interaction.response.send_message(response)


async def handle_question(trigger: discord.message.Message | discord.Reaction | discord.Interaction, user: discord.User) -> str:
	"""Handle a question message and return a matching wiki article"""
	if isinstance(trigger, discord.Reaction):
		message = trigger.message
		asked_by = user
	elif isinstance(trigger, discord.Message):
		if trigger.type == discord.MessageType.reply and trigger.reference != None and trigger.reference.cached_message != None:
			message = trigger.reference.cached_message
			asked_by = trigger.author
		else:
			return None
	elif isinstance(trigger, discord.Interaction):
		message = trigger.message
		asked_by = user
	else:
		return None

	_LOG.info(f"{ asked_by.name } is zo'n dom hondje die niet weet wat '{ message.content }' betekent")
	wiki_article = await get_article(message.content)

	if wiki_article is None:
		return "Daar heb ik nog nooit van gehoord"
	else:
		wiki_title: str = wiki_article.get('title')
		wiki_id: int = wiki_article.get('pageid')
		wiki_link: str = f"https://nl.wikipedia.org/wiki/{ urllib.parse.quote(wiki_title, safe='') }?curid={ wiki_id }"
		
		return f"Oh, '{wiki_title}'! Daar heb ik dit wel eens over gelezen:\r\n{wiki_link}"

async def get_article(query) -> dict:
	query = urllib.parse.quote(query, safe='')
	async with aiohttp.ClientSession() as http_session:
		async with http_session.get(f"https://nl.wikipedia.org/w/api.php?action=query&list=search&format=json&srsearch={query}") as response:
			wiki_response = await response.json()
	wiki_results = wiki_response.get("query", dict()).get("search", list())

	wiki_article = None
	if len(wiki_results) > 0:
		return wiki_results[0]

	return None