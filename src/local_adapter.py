from typing import Any, Self


class LocalAdapter:
    def __init__(self, correct_word: str) -> None:
        self._correct_word = correct_word
        self._guesses: list[str] = []

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args: list[Any]) -> None:
        return None

    async def close(self) -> None: ...

    async def input_submit_guess(self, word: str) -> None:
        self._guesses.append(word)

    async def check_result(self, word_index: int) -> None:
        self._guesses[-1] == self._correct_word

    async def clean_guess(self) -> None: ...

    async def fetch_row_result(self, row_index: int) -> list[str]:
        return [
            self.match_letter(self._guesses[row_index], index) for index in range(5)
        ]

    def match_letter(self, word: str, index: int) -> str:
        if self._correct_word[index] == word[index]:
            return "right"
        if word[index] in self._correct_word:
            return "place"
        return "wrong"
