"""Play a Lingo game"""
from enum import Enum
import glob
import json
import logging
import os
import random
import re

from doosbot.const import DoosBotEmoji
_LOG = logging.getLogger(__name__)

import discord
import doosbot.client

LINGO_SOUNDTRACK = "sfx/lingo/lingo_2019_{:02d}.mp3"
LINGO_GAMESCORE = "sfx/lingo/lingo_spelscore_{:02d}.mp3"

LINGO_LETTERS = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]
LINGO_WORDFILE = "words/{}/{}.txt"
LINGO_WORDSET_PATH = "words"
LINGO_WORDSETS = ["nl","pokemon"]

lingo_wordset_manifests = dict[dict]()
lingo_game_active = dict()

LINGO_WORD_MIN = 2
LINGO_WORD_MAX = 13
word_lists = dict()

def init(client: doosbot.client.DoosBotClient, tree: discord.app_commands.CommandTree):

	for word_set in next(os.walk("words"))[1]:
		word_lists[word_set] = dict()
		# Get list of files in words/{word_set}/ directory
		
		word_set_files = glob.glob( # Wie is daar?
			os.path.join(
				LINGO_WORDSET_PATH, word_set, "*.txt" # Get all .txt files in the directory
			)
		)

		# Read the wordset manifest
		manifest_file_path = os.path.join(
			LINGO_WORDSET_PATH, word_set, "manifest.json"
		
		)
		with open(manifest_file_path) as manifest_file:
			manifest = json.load(manifest_file)
			lingo_wordset_manifests[word_set] = manifest

		for word_list_file in word_set_files:
			word_list = word_list_file.split(os.sep)[-1].split(".")[0]
			with open(word_list_file) as f:
				all_words = f.read()

			word_lists[word_set][word_list] = all_words.splitlines()

	@tree.command(name="lingo", description="Lingo spelen met DoosBot :D",)
	async def command_lingo(interaction: discord.Interaction, word_set: str = "nl", word_list: str = None, word: str = None):
		_LOG.info(f"{ interaction.command.name } command executed by { interaction.user.name }")
		
		if not word_set in lingo_wordset_manifests:
			await interaction.response.send_message(f"{DoosBotEmoji.ERROR} Ik spreek geen { word_set }. Ik spreek wel:\n{ ', '.join(lingo_wordset_manifests.keys()) }")
			return
			
		manifest: dict = lingo_wordset_manifests[word_set]
		if word_list == None:
			word_list = manifest.get("default")

		if not word_list in word_lists[word_set]:
			await interaction.response.send_message(f"{DoosBotEmoji.ERROR} Ik heb geen woordenlijst { word_list } in { word_set }. Ik heb wel deze lijsten:\n{ ', '.join(word_lists[word_set].keys()) }")
			return
		
		valid_words = word_lists[word_set][
			manifest.get("valid", word_list)
		]

		if word == None:
			try:
				word = await get_random_word(word_set, word_list)
			except Exception as e:
				await interaction.response.send_message(f"{DoosBotEmoji.ERROR} Oeps, er ging iets mis bij het starten van Lingo:\n ```{e}```")
		else: # Word is rigged
			word = word.upper()
			if not all(char in set(LINGO_LETTERS) for char in word.upper()):
				await interaction.response.send_message(f"{DoosBotEmoji.ERROR} Zeg makker, als je Lingo wil riggen moet je wel alleen Lingo letters gebruiken!")
				return
		try:	
			game = LingoGame(client = client, text_channel = interaction.channel, word = word, valid_words = valid_words)
		except Exception as e:
			await interaction.response.send_message(f"{DoosBotEmoji.ERROR} Oeps, er ging iets mis bij het starten van Lingo:\n ```{e}```")
		await interaction.response.send_message(f"Het is tijd voor Lingo!\nIk heb een {len(word)}-letterwoord:\n{ text_to_emoji(game.guess_suggestion) }")


		if interaction.user.voice != None:
			voice_channel = interaction.user.voice.channel
			await game.play_music(12, LINGO_SOUNDTRACK, voice_channel)

	@client.listen('on_message')
	async def on_message(message: discord.message.Message):
		if message.author == client.user:
			return
		if message.channel in lingo_game_active:
			if isinstance(lingo_game_active[message.channel], LingoGame):
				game: LingoGame = lingo_game_active[message.channel]
				await game.handle_guess(message)

class LingoGame():
	def __init__(self, client: doosbot.client.DoosBotClient, text_channel: discord.TextChannel, word: str, valid_words: list[str]):
		self.client = client
		self.text_channel = text_channel
		self.word = word.upper()
		self.valid_words = valid_words
		lingo_game_active[text_channel] = self
		
		self._guess_count = 0
		self._guess_suggestion = f"{word[0]:{'_'}{'<'}{len(word)}}" # Initialize with first letter of word and rest as underscores
		self._last_suggestion_message: discord.Message = None

	async def play_music(self, soundtrack_id: int, soundtrack_type: str, voice_channel: discord.VoiceChannel, loop: bool = False):
		await self.client.play_file(soundtrack_type.format(soundtrack_id), voice_channel, loop=loop)

	async def handle_guess(self, message: discord.Message):
		guess = LingoScore(self.word, message.content, self.valid_words)

		# Stop the game if guess is correct
		if guess.is_correct:
			await self.stop()

		if not guess.is_valid:
			return
		else:
			self._guess_count += 1
			await message.reply(f"{ text_to_emoji(guess.guess) }\n{guess.score_string }")
			# TODO play scoring beeps

		# Change playing music if author is in a voice channel
		if message.author.voice != None:
			voice_channel = message.author.voice.channel
			if guess.is_correct:
				await self.play_music(5, LINGO_SOUNDTRACK, voice_channel)
				
			else:
				await self.play_music(1 + (self._guess_count % 12), LINGO_GAMESCORE, voice_channel, loop = True)
		
		# Remove previous suggestion message
		if self._last_suggestion_message:
			try:
				await self._last_suggestion_message.delete()
			except:
				pass


		# Reply suggestion or congratulation
		if guess.is_correct:
			await message.reply("Joepie de poepie, je hebt het woord geraden!")
		else:
			self._guess_suggestion = merge_suggestions(self._guess_suggestion, guess.suggestion)
			self._last_suggestion_message = await message.channel.send(text_to_emoji(self._guess_suggestion))

	async def stop(self):
		lingo_game_active[self.text_channel] = False
	
	@property 
	def guess_suggestion(self):
		return self._guess_suggestion
	
class LingoScore():
	def __init__(self, word: str, guess: str, valid_words: list[str]):
		self.valid_words = valid_words
		self.word = word.upper()
		self.guess = guess.upper()
		self._suggestion = ""

		score = ""

		if letter_count(self.word) == letter_count(self.guess):
			used_letter_count = dict()
			for letter in LINGO_LETTERS:
				used_letter_count[letter] = 0

			for index in range(len(self.word)):
				if self.word[index] == self.guess[index]:
					used_letter_count[self.guess[index]] += 1
					self._suggestion += self.guess[index]
				else:
					self._suggestion += "_"

			for index in range(len(self.word)):
				if self.word[index] == self.guess[index]:
					score += LingoEmoji.CORRECT

				elif self.word.count(self.guess[index]) > used_letter_count[self.guess[index]]:
					used_letter_count[self.guess[index]] += 1
					score += LingoEmoji.WRONG_POSITION
					
				else:
					score += LingoEmoji.INCORRECT
				score += " "
					
		self._score_string = score

	@property
	def is_valid(self):
		word_length = letter_count(self.word)
		guess_length = letter_count(self.guess)
		if guess_length != word_length:
			return False
		elif self.word == self.guess:
			return True
		elif self.guess not in self.valid_words:
			return False
		else:
			return True

	
	@property
	def is_correct(self):
		return self.word == self.guess

	@property
	def score_string(self):
		return self._score_string
	
	@property
	def suggestion(self):
		return self._suggestion
		

class LingoEmoji(str, Enum):
	CORRECT = "🟥"
	WRONG_POSITION = "🟡"
	INCORRECT = "🟦"


async def get_random_word(word_set: str, word_list: str):
	all_words = word_lists[word_set][word_list]
	num_words = len(all_words)
	word_index = random.randint(0, num_words - 1)
	random_word = all_words[word_index]

	return random_word.upper()

def letter_count(word: str):
	count = len(word)

	# Count IJ as single letter
	# count -= word.count("ij")
	return count

def text_to_emoji(text: str):
	emoji_string = ""
	for character in text.upper():
		if character in LINGO_LETTERS:
			emoji_character = chr(ord(character) + ord("🇦") - ord("A"))
		elif character == "_":
			emoji_character = "🟦"

		emoji_string += emoji_character + " "
	
	return emoji_string

def merge_suggestions(suggestion1, suggestion2) -> str:
	result = ""
	for index in range(len(suggestion2)):
		if suggestion2[index] != "_":
			result += suggestion2[index]
		else:
			result += suggestion1[index]

	return result
