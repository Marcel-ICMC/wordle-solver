import pytest_asyncio

from adapters import TermoAdapter
from game import Game


@pytest_asyncio.fixture(scope="session")
async def answer() -> str:
    async with await TermoAdapter.create(headless=True) as adapter:
        game = Game(game_adapter=adapter)
        for _ in range(6):
            result = await game.guess("termo")
            if result == 1:
                return "termo"

        return await game.get_answer_after_loss()
