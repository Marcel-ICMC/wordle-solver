import pytest

from adapters import TermoAdapter
from game import Game


@pytest.fixture
async def pytest_configure(scope: str = "session") -> str:
    # Dynamically generate a unique identifier for this test run
    adapter = await TermoAdapter.create()
    game = Game(game_adapter=adapter)
    for _ in range(6):
        await game.guess("termo")

    return await game.get_answer_after_loss()
