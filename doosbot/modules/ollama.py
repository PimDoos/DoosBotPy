"""Talk to Ollama models."""
import logging
_LOG = logging.getLogger(__name__)

import doosbot.client
from doosbot.const import DoosBotEmoji
import discord
from ollama import AsyncClient, ChatResponse, GenerateResponse
from config import OLLAMA_HOST, OLLAMA_MODEL, OLLAMA_SYSTEM_PROMPT

def init(client: doosbot.client.DoosBotClient, tree: discord.app_commands.CommandTree):
    _LOG.info("Initializing Ollama module")

    @tree.command(name="lama", description = "Chatten met DoosBot")
    async def command_chat(interaction: discord.Interaction, message: str):
        _LOG.info(f"{ interaction.command.name} command executed by { interaction.user.name }")
        await interaction.response.defer(thinking=True)
        try:
            response = await ask_ollama(client, OLLAMA_MODEL, message, interaction)
            await interaction.followup.send(response)
        except Exception as e:
            _LOG.error(f"Error asking Ollama model: {e}")
            await interaction.followup.send(f"{DoosBotEmoji.ERROR} Oepsie poepsie, er ging iets mis met dit commando: {e}")
    
    _LOG.info("Nou het is gelukt hoor, ik heb Ollama geladen!")
        
async def ask_ollama(client: doosbot.client.DoosBotClient, model: str, message: str, interaction: discord.Interaction) -> str:
    """Ask an Ollama model a question."""
    ollama_client = AsyncClient(host=OLLAMA_HOST)
    prompt = f"{OLLAMA_SYSTEM_PROMPT}\n{interaction.user.name}: {message}"
    response = await ollama_client.generate(model=model, prompt=prompt, stream=False)
    return response.response

    