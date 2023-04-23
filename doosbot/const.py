import enum


SFX_DIRECTORY = "sfx/{}"
TEMPDIR = "tmp/{}"
BUFFER_TTS = TEMPDIR.format("tts.mp3")
BUFFER_YOUTUBE = TEMPDIR.format("yt.m4a")

class DoosBotEmoji(str, enum.Enum):
	OK = "✅"
	ERROR = "❌"
	SEARCH = "🔎"
	VOLUME = "🔉"