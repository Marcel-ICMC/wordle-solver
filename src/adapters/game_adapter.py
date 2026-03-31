from typing import Protocol


class GameAdapter(Protocol):
    """
    Simple adapter that receives a 5-letter guessed word
    Returns a list with 5 element each being either
    - "right": letter is correctly placed
    - "place": letter is in the word but not in the correct place
    - "wrong": letter is not in the word
    """

    async def input_submit_guess(self, word: str) -> list[str]: ...

    async def get_answer(self) -> str: ...
