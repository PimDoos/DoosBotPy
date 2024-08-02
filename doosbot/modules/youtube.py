import logging
_LOG = logging.getLogger(__name__)

import discord
import doosbot.client
from doosbot.const import *

import asyncio
import os
import functools
import yt_dlp

def init(client: doosbot.client.DoosBotClient, tree: discord.app_commands.CommandTree):

	@tree.command(name="yt", description = "Zoek op YouTube")
	async def command_youtube_search(interaction: discord.Interaction, query: str):
		_LOG.info(f"{ interaction.command.name } command executed by { interaction.user.name }")
		if interaction.user.voice != None:
			media_channel = interaction.user.voice.channel
			await interaction.response.defer(thinking=True)
			try:
				video_info = await download(query, BUFFER_YOUTUBE)
				if video_info is None:
					await interaction.followup.send(f"{DoosBotEmoji.ERROR} Zeg die video kan ik niet vinden")
				else:
					await interaction.followup.send(f"Ik zal '{ video_info.get('title') }' dan maar gaan afspelen")
					await client.play_file(BUFFER_YOUTUBE, media_channel)
			except Exception as e:
				await interaction.followup.send(f"{DoosBotEmoji.ERROR} Er ging iets stuk: { e }")
		else:
			await interaction.followup.send(f"{DoosBotEmoji.ERROR} Je zit niet in een voice channel kuthoofd")


async def download(query: str, output_file: str, file_format: str = "m4a/bestaudio/best") -> str:
	_LOG.info(f"Searching YTDL for query: '{ query }'")
	event_loop = asyncio.get_event_loop()

	ytdl = yt_dlp.YoutubeDL({"format":file_format,"default_search":"ytsearch","extractaudio":True,"noplaylist":True,"outtmpl":output_file})
	partial = functools.partial(ytdl.extract_info, query)

	if os.path.exists(output_file):
		delete_file = functools.partial(os.remove, output_file)
		await event_loop.run_in_executor(None, delete_file)
	
	search_data = await event_loop.run_in_executor(None, partial)
	
	if "entries" not in search_data:
		search_info = search_data
	else:
		for entry in search_data["entries"]:
			if entry:
				search_info = entry
				break
		if search_info is None:
			_LOG.info(f"No results found")
			return None

	video_info = search_info
	_LOG.info(f"Found video with title '{ video_info.get('title') }'")
	return video_info
