"""Read articles from wikipedia"""
import logging
_LOG = logging.getLogger(__name__)

import discord
import doosbot.client
from doosbot.const import *

import aiohttp
import urllib.parse

def init(client: doosbot.client.DoosBotClient, tree: discord.app_commands.CommandTree):

	@tree.command(name="wiki", description = "Zoek op Wikipedia")
	async def command_get_article(interaction: discord.Interaction, query: str):
		_LOG.info(f"{ interaction.command.name } command executed by { interaction.user.name }")
		wiki_article = await get_article(query)

		if wiki_article is None:
			await interaction.response.send_message(f"{DoosBotEmoji.ERROR} Die onzin ken ik niet")
		else:
			wiki_title: str = wiki_article.get('title')
			wiki_id: int = wiki_article.get('pageid')
			wiki_link: str = f"https://nl.wikipedia.org/wiki/{ urllib.parse.quote(wiki_title, safe='') }?curid={ wiki_id }"
			
			await interaction.response.send_message(f"Ah ja, '{wiki_title}'! Daar heb ik dit wel eens over gelezen:\r\n{wiki_link}")


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