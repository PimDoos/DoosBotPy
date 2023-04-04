"""Roll a dice"""
import logging
_LOG = logging.getLogger(__name__)

from random import randint
import discord
import doosbot.client

def init(client: doosbot.client.DoosBotClient, tree: discord.app_commands.CommandTree):
	
	@tree.command(name="dobbeltenen", description="Rol met mijn dobbeltenen")
	async def command_dice(interaction: discord.Interaction):
		_LOG.info(f"{ interaction.command.name } command executed by { interaction.user.name }")
		result = randint(1,6)
		await interaction.response.send_message(f"Ik heb gerold met mijn dobbeltenen en het antwoord is: { result }")