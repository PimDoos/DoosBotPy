"""Play a quiz game"""
import logging
import random
from enum import StrEnum

import discord

import doosbot.client
from doosbot.const import DoosBotEmoji

_LOG = logging.getLogger(__name__)

# Determine the music to play based on the current level of the game
MAX_LEVEL = 5
level = 0

def init(client: doosbot.client.DoosBotClient, tree: discord.app_commands.CommandTree):

    # /quiz
    # MODE: custom questions
    # question: the question
    # answer
    # MODE: baked questions
    # get the question and correct answers from somewhere


    @tree.command(name="quiz", description="Wie wil miljonair zijn met DoosBot :D")
    async def command_quiz(
        interaction: discord.Interaction, question: str, correct_answer: str, answer_1: str, answer_2: str, answer_3: str,
    ):
        _LOG.info(f"{ interaction.command.name } command executed by { interaction.user.name }")

        answers = [correct_answer, answer_1, answer_2, answer_3]

        # Check if all answers are unique
        if len(set(answers)) != len(answers):
            await interaction.response.send_message(f"{DoosBotEmoji.ERROR} Alle antwoorden moeten uniek zijn")
            return

        # Shuffle the answers and get the index of the correct answer
        random.shuffle(answers)

        correct_answer_id = answers.index(correct_answer)
        quiz_game = QuizGame(client, interaction, question, answers, correct_answer_id)
        await quiz_game.create_poll()


# Helper functions
def get_answer_index_emoji(answer_index: int) -> str:
    """Get the emoji for the answer index"""
    return chr(0x1F1E6 + answer_index)  # A = 0x1F1E6, B = 0x1F1E7, C = 0x1F1E8, D = 0x1F1E9

class QuizSoundtrackType(StrEnum):
    LETS_PLAY = "sfx/millionaire/letsplay-{:02d}.mp3"
    QUESTION = "sfx/millionaire/question-{:02d}.mp3"
    FINAL_ANSWER = "sfx/millionaire/finalanswer-{:02d}.mp3"
    WIN = "sfx/millionaire/win-{:02d}.mp3"
    LOSE = "sfx/millionaire/lose-{:02d}.mp3"
    LIFELINE = "sfx/millionaire/lifeline-{:02d}.mp3"

class QuizPollView(discord.ui.LayoutView):
    def __init__(self, game: "QuizGame"):
        super().__init__()
        self.game = game
        self.buttons = []
        self.add_item(
            discord.ui.TextDisplay(
                content=game.question,
            )
        )
        self.action_row = discord.ui.ActionRow()

        for i in range(len(game.answers)):
            self.add_answer_button(i)

        self.add_item(self.action_row)

    def add_answer_button(self, answer_index: int):
        button = discord.ui.Button(
            emoji=get_answer_index_emoji(answer_index),
            label=self.game.answers[answer_index],
            style=discord.ButtonStyle.primary,
            custom_id=str(answer_index),
        )
        
        async def submit(interaction: discord.Interaction):
            await self.game.submit_answer(interaction, answer_index)

        button.callback = submit

        self.buttons.append(button)
        self.action_row.add_item(button)

    def disable_buttons(self):
        for button in self.buttons:
            button.disabled = True


class QuizGame:

    def __init__(self, client: doosbot.client.DoosBotClient, interaction: discord.Interaction, question: str, answers: list, correct_answer_id: int):
        self.client = client
        self.interaction: discord.Interaction = interaction

        global level
        level = level + 1 % MAX_LEVEL
        self.level = level

        # Question and answers
        self.question = question
        self.answers = answers
        self.correct_answer_id = correct_answer_id
        self.correct_answer = answers[correct_answer_id]

        self.poll_view: QuizPollView | None = None

        self.is_active = True


    async def create_poll(self):
        """Create the poll to store answers"""
        self.poll_view = QuizPollView(self)

        await self.interaction.response.send_message(view=self.poll_view)

        if self.interaction.user.voice != None:
            voice_channel = self.interaction.user.voice.channel
            _LOG.info(f"User { self.interaction.user.name } is in a voice channel, playing music for quiz game (level {self.level})")

            await self.play_music(self.level % MAX_LEVEL, QuizSoundtrackType.QUESTION, voice_channel, loop=True, intro_id=self.level % MAX_LEVEL, intro_type=QuizSoundtrackType.LETS_PLAY)
        else:
            _LOG.info(f"User { self.interaction.user.name } is not in a voice channel, skipping music playback")

    async def submit_answer(self, button_interaction: discord.Interaction, answer_index: int):
        """Submit an answer"""

        if not self.is_active:
            await button_interaction.response.pong()
        else:
            self.is_active = False
            self.poll_view.disable_buttons()

        if button_interaction.user.voice != None:
            voice_channel = button_interaction.user.voice.channel
        else:
            voice_channel = None

        if answer_index == self.correct_answer_id:
            # Correct answer
            if self.interaction.response.is_done() and self.poll_view:
                self.poll_view.buttons[answer_index].style = discord.ButtonStyle.success
                await self.interaction.edit_original_response(view=self.poll_view)
                await button_interaction.response.send_message(f"{DoosBotEmoji.OK} {button_interaction.user.mention}")

                if voice_channel != None:
                    await self.play_music(self.level + 1, QuizSoundtrackType.WIN, voice_channel)

        else:
            # Incorrect answer
            if self.interaction.response.is_done() and self.poll_view:
                # Mark incorrect answer
                self.poll_view.buttons[answer_index].style = discord.ButtonStyle.danger

                # Mark correct answer
                self.poll_view.buttons[self.correct_answer_id].style = discord.ButtonStyle.success
                
                await self.interaction.edit_original_response(view=self.poll_view)
                await button_interaction.response.send_message(f"{DoosBotEmoji.ERROR} {button_interaction.user.mention}")

                if voice_channel != None:
                    await self.play_music(self.level + 1, QuizSoundtrackType.LOSE, voice_channel)


    async def play_music(self, soundtrack_id: int, soundtrack_type: QuizSoundtrackType, voice_channel: discord.VoiceChannel, loop: bool = False, intro_id: int | None = None, intro_type: QuizSoundtrackType | None = None):
        file_name_1 = soundtrack_type.format(soundtrack_id)
        file_name_2 = intro_type.format(intro_id) if intro_type and intro_id else None
        await self.client.play_file(file_name_1, voice_channel, loop=loop, file_name_2=file_name_2)

    # Lifelines
    async def lifeline_50_50(self):
        """Remove 2 incorrect answers"""
        pass

    async def lifeline_phone_a_friend(self):
        """Ask a friend for help"""
        pass


    