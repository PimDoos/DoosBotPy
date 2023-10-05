"""Control media volume"""
import logging
_LOG = logging.getLogger(__name__)

import os
import re
import discord
import doosbot.client
from doosbot.const import *
from config import JOIN_FX

def init(client: doosbot.client.DoosBotClient, tree: discord.app_commands.CommandTree):

	@tree.command(name="vol", description = "Volume")
	async def command_volume(interaction: discord.Interaction, volume_pct: int):
		_LOG.info(f"{ interaction.command.name } command executed by { interaction.user.name }")
		if interaction.user.voice != None:
			media_channel = interaction.user.voice.channel
			if volume_pct >= 0 and volume_pct <= 100:
				volume = volume_pct / 100
				await client.set_volume(volume)
				await interaction.response.send_message(f"{DoosBotEmoji.VOLUME} {volume_pct} %")
			else:
				await interaction.response.send_message(f"Het volume kan maximaal op 100, anders gaan je oren naar de tjering")
		else:
			await interaction.response.send_message(f"Je zit niet in een voice channel kuthoofd")

	@tree.command(name="leeg", description = "Leeglume")
	async def command_volume_inverted(interaction: discord.Interaction, volume_pct: int):
		await command_volume(interaction, 100 - volume_pct)
	
	@tree.command(name="kwark", description = "Hoe vol is de kwark?")
	async def command_volume_get(interaction: discord.Interaction):
		_LOG.info(f"{ interaction.command.name } command executed by { interaction.user.name }")
		if client._volume_level > 0.65:
			await interaction.response.send_message(f"https://static.ah.nl/dam/product/AHI_43545239373933323833?revLabel=2&rendition=800x800_JPG_Q90&fileType=binary")
		elif client._volume_level > 0.35:
			await interaction.response.send_message(f"https://static.ah.nl/dam/product/AHI_43545239363736393839?revLabel=1&rendition=800x800_JPG_Q90&fileType=binary")
		else:
			await interaction.response.send_message(f"https://static.ah.nl/dam/product/AHI_43545239363737303438?revLabel=1&rendition=800x800_JPG_Q90&fileType=binary")

	@tree.command(name="tts", description="Zeg dingen")
	async def command_tts(interaction: discord.Interaction, text: str):
		_LOG.info(f"{ interaction.command.name } command executed by { interaction.user.name }")
		if interaction.user.voice != None:
			media_channel = interaction.user.voice.channel

			await interaction.response.defer(thinking=True)
			await client.play_tts(text, media_channel)
			await interaction.followup.send(text)
		else:
			await interaction.response.send_message(f"{DoosBotEmoji.ERROR} Je zit niet in een voice channel kuthoofd")

	@tree.command(name="sfx", description="Maak gekke geluidjes")
	async def command_sfx(interaction: discord.Interaction, query: str):
		_LOG.info(f"{ interaction.command.name } command executed by { interaction.user.name }")
		if interaction.user.voice != None:
			media_channel = interaction.user.voice.channel

			await interaction.response.defer(thinking=True)
			for file in os.listdir(SFX_DIRECTORY.format("")):
				if re.search(query, file) != None:
					file_name = SFX_DIRECTORY.format(file)
					await client.play_file(file_name, media_channel)
					await interaction.followup.send(f"Ik zal `{file}` dan maar gaan afspelen")
					break
			else:
				await interaction.followup.send(f"{DoosBotEmoji.ERROR} Ja zeg dat bestand kan ik niet vinden")
		else:
			await interaction.response.send_message(f"{DoosBotEmoji.ERROR} Je zit niet in een voice channel kuthoofd")

	@tree.command(name="stop", description="Stop met afspelen en sluit het voice kanaal")
	async def command_stop(interaction: discord.Interaction):
		_LOG.info(f"{ interaction.command.name } command executed by { interaction.user.name }")
		if interaction.user.voice != None:
			media_channel = interaction.user.voice.channel

			voice_client = client.get_voice_client(media_channel)

			if voice_client != None:
				await voice_client.disconnect()
				await interaction.response.send_message(f"OK DOEI")
			else:
				await interaction.response.send_message(f"{DoosBotEmoji.ERROR} Ik zit niet in een voice channel kuthoofd")
		else:
			await interaction.response.send_message(f"{DoosBotEmoji.ERROR} Je zit niet in een voice channel kuthoofd")
		
	@client.event
	async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
		if before.channel == None and after.channel != None:
			sfx_file = JOIN_FX["default"]
			if member.id in JOIN_FX:
				sfx_file = JOIN_FX[member.id]
			
			if sfx_file != None:
				await client.play_file(sfx_file, after.channel)
		elif after.channel == None and before.channel != None:
			if len(before.channel.members) == 1:
				voice_client = client.get_voice_client(before.channel)

				if voice_client != None:
					await voice_client.disconnect()

	