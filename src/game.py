import unicodedata
from typing import Any, Self

from exceptions import InvalidWordError, LengthWordlError, NotAlphaWordError
from game_adapter import GameAdapter


class Game:
    def __init__(self, browser: GameAdapter):
        self._browser = browser
        self.guesses: list[str] = []
        self.results: list[list[str]] = []
        self.result: int = 0
        self.word_index: int = 0

    def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *args: list[Any]) -> None:
        await self.close()
        return None

    async def close(self) -> None:
        await self._browser.close()

    async def guess(self, word: str) -> int:
        self._validates_word(word)

        try:
            await self._browser.input_submit_guess(self._strip_accents(word))
            await self._browser.check_result(self.word_index)
        except InvalidWordError:
            print("Invalid word")
            await self._browser.clean_guess()

        await self._update_result()

        self.guesses.append(word)
        self.word_index += 1

        return self.result

    def _validates_word(self, word: str) -> None:
        if len(word) != 5:
            raise LengthWordlError(f"Word should be exactly 5 characters, not {word}")

        if not word.isalpha():
            raise NotAlphaWordError(
                f"Word should contain only alphabetical characters, not {word}"
            )

    async def _update_result(self) -> None:
        word_result = await self._browser.fetch_row_result(self.word_index)
        self.results.append(word_result)
        self.result = self._check_win()

    def _check_win(self) -> int:
        if all(r == "right" for r in self.results[-1]):
            return 1
        if len(self.results) == 6:
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
