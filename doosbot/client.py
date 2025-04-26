import discord
from discord.ext.commands import Bot
import logging
_LOG = logging.getLogger(__name__)

from gtts import gTTS
from doosbot.const import BUFFER_TTS

class DoosBotClient(Bot):

	_volume_level = 0.25
	_active_media = None

	async def on_ready(self):
		_LOG.info(f"Connected to Discord with identity { self.user }")
		await self.tree.sync()

	async def on_message(self, message: discord.message.Message):
		_LOG.info(f"MESSAGE { message.author.display_name }→{self.user.display_name}: { message.content }")
	
	def get_voice_client(self, channel) -> discord.VoiceClient:
		voice_client: discord.VoiceClient = None
		for voice_client in self.voice_clients:
			if voice_client.channel == channel:
				break
		
		return voice_client

	async def play_file(self, file_name, channel: discord.VoiceChannel, loop: bool = False):
		voice_client = self.get_voice_client(channel)
		if voice_client == None:
			voice_client = await channel.connect()
		voice_client.stop()

		if loop:
			media = discord.FFmpegPCMAudio(file_name, before_options="-stream_loop -1")
		else: 
			media = discord.FFmpegPCMAudio(file_name)
		media_volume = discord.PCMVolumeTransformer(media, self._volume_level)
		self._active_media = media_volume
		voice_client.play(media_volume)
	
	async def set_volume(self, volume):
		self._volume_level = volume
		if self._active_media != None:
			self._active_media.volume = self._volume_level
