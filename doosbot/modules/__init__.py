import logging
_LOG = logging.getLogger(__name__)

import doosbot.client
import doosbot.modules.chat
import doosbot.modules.dice
import doosbot.modules.lingo
import doosbot.modules.tts
import doosbot.modules.voice
import doosbot.modules.wikipedia
import doosbot.modules.youtube


def init(client: doosbot.client.DoosBotClient):
	doosbot.modules.chat.init(client, client.tree)	
	doosbot.modules.dice.init(client, client.tree)
	doosbot.modules.lingo.init(client, client.tree)
	doosbot.modules.tts.init(client, client.tree)
	doosbot.modules.voice.init(client, client.tree)
	doosbot.modules.wikipedia.init(client, client.tree)
	doosbot.modules.youtube.init(client, client.tree)
	