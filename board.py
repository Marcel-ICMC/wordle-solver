from typing import Any
from typing_extensions import Self
import unicodedata

from board_browser import BoardBrowser
from exceptions import InvalidWordError, LengthWordlError, NotAlphaWordError


class Board:
    def __init__(self, headless: bool = True):
        self._browser = BoardBrowser(headless)
        self.guesses: list[str] = []
        self.results: list[list[str]] = []
        self.result: int = 0
        self.word_index: int = 0

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args: list[Any]) -> None:
        self.close()
        return None

    def close(self) -> None:
        self._browser.close()

    def guess(self, word: str) -> int:
        self._validates_word(word)

        try:
            self._browser.input_submit_guess(self._strip_accents(word))
            self._browser.check_result(self.word_index)
        except InvalidWordError:
            print("Invalid word")
            self._browser.clean_guess()

        self._update_result()

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

    def _update_result(self) -> None:
        row_result = self._browser.fetch_row_result(self.word_index)
        word_result = self._parse_row_result(row_result)
        self.results.append(word_result)
        self.result = self._check_win()

    def _parse_row_result(self, row_result: str) -> list[str]:
        return [c.split()[1] for c in row_result]

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
