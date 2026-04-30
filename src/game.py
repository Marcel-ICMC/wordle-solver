import string
import unicodedata

from adapters import GameAdapter
from exceptions import (
    GameNotFinishedError,
    InvalidWordError,
    LengthWordError,
    NotAlphaWordError,
)


class Game:
    def __init__(self, game_adapter: GameAdapter):
        self._game_adapter = game_adapter
        self.guesses: list[str] = []
        self.remaining: set[str] = set(string.ascii_lowercase)
        self.known_positions: list[str] = ["_", "_", "_", "_", "_"]
        self.misplaced: dict[str, set[int]] = {}

        self.result: int = 0
        self.word_index: int = 0

    async def guess(self, guess: str) -> int:
        self._validates_word(guess)
        normalized_guess = self._strip_accents(guess).lower()

        try:
            word_result = await self._game_adapter.input_submit_guess(normalized_guess)
            await self._update_game(normalized_guess, word_result)
        except InvalidWordError:
            return -2

        self.guesses.append(normalized_guess)
        self.word_index += 1

        self.result = self._check_win(word_result)
        return self.result

    def _validates_word(self, guess: str) -> None:
        if len(guess) != 5:
            raise LengthWordError(f"Word should be exactly 5 characters, not {guess}")

        if not guess.isalpha():
            raise NotAlphaWordError(
                f"Word should contain only alphabetical characters, not {guess}"
            )

    async def _update_game(self, guess: str, word_result: list[str]) -> None:
        for i in range(5):
            self.remaining.discard(guess[i])

            if word_result[i] == "place":
                self.misplaced.setdefault(guess[i], set()).add(i)

            if word_result[i] == "right":
                self.known_positions[i] = guess[i]

    async def get_answer_after_loss(self) -> str:
        if len(self.guesses) != 6:
            raise GameNotFinishedError("Can't get answer without finishing the game")

        return await self._game_adapter.get_answer()

    def _check_win(self, word_result: list[str]) -> int:
        if all(r == "right" for r in word_result):
            return 1
        if len(self.guesses) == 6:
            return -1
        return 0

    @staticmethod
    def _strip_accents(text: str) -> str:
        return "".join(
            c
            for c in unicodedata.normalize("NFD", text)
            # "Mn" means Nonspacing_Mark
            # Check https://www.unicode.org/reports/tr44/tr44-34.html#General_Category_Values
            if unicodedata.category(c) != "Mn"
        )
