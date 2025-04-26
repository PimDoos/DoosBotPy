"""Read text to speech"""
import logging
_LOG = logging.getLogger(__name__)

from gtts import gTTS

from doosbot.const import BUFFER_TTS, DoosBotEmoji
from doosbot.client import DoosBotClient
import discord

def init(client: DoosBotClient, tree: discord.app_commands.CommandTree):

    @tree.command(name="tts", description="Zeg dingen")
    async def command_tts(interaction: discord.Interaction, text: str, lang: str = "nl", engine: str = "google"):
        """Play a text to speech message in the voice channel of the user"""

        _LOG.info(f"{ interaction.command.name } command executed by { interaction.user.name }")
        if interaction.user.voice != None:
            media_channel = interaction.user.voice.channel

            await interaction.response.defer(thinking=True)
            await play_tts(text, media_channel, lang, engine)
            await interaction.followup.send(text)
        else:
            await interaction.response.send_message(f"{DoosBotEmoji.ERROR} Je zit niet in een voice channel kuthoofd")

async def play_tts(client: DoosBotClient, text, channel: discord.VoiceChannel, lang="nl", engine="google"):
    if engine == "google":
        gTTS(text, lang=lang).save(BUFFER_TTS)
        await client.play_file(BUFFER_TTS, channel)
    # TODO implement piper TTS
    else:
        raise ValueError(f"Unknown TTS engine: {engine}")