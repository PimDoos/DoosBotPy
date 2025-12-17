"""Roll a dice"""
import logging

from doosbot.const import DoosBotEmoji
_LOG = logging.getLogger(__name__)

from random import randint
import discord
import doosbot.client

def init(client: doosbot.client.DoosBotClient, tree: discord.app_commands.CommandTree):
	
	@tree.command(name="d", description="Rol met mijn dobbeltenen")
	async def command_dice(interaction: discord.Interaction, die_size: int = 6, rolls: int = 1):
		_LOG.info(f"{ interaction.command.name } command executed by { interaction.user.name }")
		roll_results = []
		for _ in range(rolls):
			roll = randint(1, die_size)
			roll_results.append(roll)

		await interaction.response.send_message(f" { DoosBotEmoji.DICE } Ik heb { rolls }x gedobbeld met mijn dobbeltenen ({ die_size } tenen) en dit zijn de resultaten: \n1. { '\n1. '.join(map(str, roll_results)) }")
	