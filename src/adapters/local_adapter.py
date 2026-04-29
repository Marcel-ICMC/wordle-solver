from exceptions import GameNotFinishedError


class LocalAdapter:
    def __init__(self, answer: str) -> None:
        self._answer = answer
        self._guesses: list[str] = []

    async def input_submit_guess(self, word: str) -> list[str]:
        self._guesses.append(word)

        return [self._match_letter(self._guesses[-1], index) for index in range(5)]

    async def get_answer(self) -> str:
        if len(self._guesses) < 6:
            raise GameNotFinishedError("Can't get answer without finishing the game")
        return self._answer

    def _match_letter(self, word: str, index: int) -> str:
        if self._answer[index] == word[index]:
            return "right"
        if word[index] in self._answer:
            return "place"
        return "wrong"
