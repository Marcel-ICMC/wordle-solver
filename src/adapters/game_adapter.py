from typing import Protocol


class GameAdapter(Protocol):
    async def input_submit_guess(self, word: str) -> list[str]: ...
