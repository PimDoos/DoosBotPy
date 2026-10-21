"""Roll a dice"""
import logging

from doosbot.const import DoosBotEmoji
_LOG = logging.getLogger(__name__)

from random import randint
import discord
import discord.ext.commands
import doosbot.client

import regex

def init(client: doosbot.client.DoosBotClient, tree: discord.app_commands.CommandTree):

	async def command_dice(
		interaction: discord.Interaction, 
		die_size: int = 20, 
		rolls: int = 1,
	):
		_LOG.info(f"{ interaction.command.name } command executed by { interaction.user.name }")

		_LOG.info(f"Parameters: {interaction.command}")
		try:
			response = await roll_dice(die_size, rolls)
			await interaction.response.send_message(response)
		except Exception as e:
			_LOG.error(f"Error executing { interaction.command.name } command: { e }")
			await interaction.response.send_message(f" { DoosBotEmoji.ERROR } Teerlingzooi, ik laat spontaan mijn dobbeltenen vallen: { e }")

	async def roll_dice(die_size, rolls):
		roll_results = []

		if die_size < 1:
			return f" { DoosBotEmoji.ERROR } Dobbelen met null is flauwe lul"
		elif rolls < 1:
			return "Oké dan doe ik wel niets"
		elif die_size > 10000:
			return f"Een dobbelteen met { die_size } kanten? Dat is eigenlijk gewoon een bal"
		elif rolls > 100:
			return f"Ik heb helemaal geen zin om { rolls } keer te dobbelen."
		else:
			for _ in range(rolls):
				roll = randint(1, die_size)
				roll_results.append(roll)

			return f" { DoosBotEmoji.DICE } Ik heb { rolls }x gedobbeld met mijn dobbeltenen ({ die_size } tenen) en dit zijn de resultaten: \n1. { '\n1. '.join(map(str, roll_results)) }"
		

	@client.listen('on_message')
	async def on_message(message: discord.message.Message):
		command_prefix = ("gooi","werp","flikker","tyf","knikker","yeet","throw","dobbel","roll","rol","pleur","smijt","slinger","kwak","sodemieter","deponeer")
		if message.content.startswith(command_prefix):
			_LOG.info(f"{ message.author.name } tried throwing dice")
			actual_command_prefix = message.content.split(" ")[0]

			throw_parameters = message.content.removeprefix(actual_command_prefix).strip()
			throw_match = regex.match("^(\\d{0,2})d(\\d{1,3})$",throw_parameters)
			if throw_match:
				rolls_group = throw_match.group(1)
				if len(rolls_group) == 0:
					rolls = "1"
				else:
					rolls = rolls_group
				die_size = throw_match.group(2)

				if rolls.isdigit() and die_size.isdigit():
					response = await roll_dice(die_size=int(die_size), rolls=int(rolls))
					await message.reply(response)


	command = discord.app_commands.Command(
		name="d",
		description="Rol met mijn dobbeltenen",
		callback = command_dice,
	)
	
	tree.add_command(command)