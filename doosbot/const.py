import enum


SFX_DIRECTORY = "sfx/{}"
BUFFER_TTS = "tts.mp3"
BUFFER_YOUTUBE = "yt.m4a"

class DoosBotEmoji(str, enum.Enum):
	OK = "✅"
	ERROR = "❌"
	SEARCH = "🔎"
	VOLUME = "🔉"