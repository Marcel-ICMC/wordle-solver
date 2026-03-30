class LocalAdapter:
    def __init__(self, answer: str) -> None:
        self._answer = answer
        self._guesses: list[str] = []

    async def input_submit_guess(self, word: str) -> list[str]:
        self._guesses.append(word)

        return await self._fetch_row_result()

    async def _fetch_row_result(self) -> list[str]:
        return [self._match_letter(self._guesses[-1], index) for index in range(5)]

    def _match_letter(self, word: str, index: int) -> str:
        if self._answer[index] == word[index]:
            return "right"
        if word[index] in self._answer:
            return "place"
        return "wrong"
