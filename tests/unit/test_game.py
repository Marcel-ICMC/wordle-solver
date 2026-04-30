import pytest

from adapters import LocalAdapter
from exceptions import LengthWordError, NotAlphaWordError
from game import Game


@pytest.mark.asyncio
async def test_guess_increments_word_index() -> None:
    game = Game(game_adapter=LocalAdapter(answer="carro"))
    await game.guess("carro")
    assert game.word_index == 1


@pytest.mark.asyncio
async def test_correct_guess_returns_win() -> None:
    game = Game(game_adapter=LocalAdapter(answer="carro"))
    result = await game.guess("carro")
    assert result == 1


@pytest.mark.asyncio
async def test_correct_guess_updates_game_result() -> None:
    game = Game(game_adapter=LocalAdapter(answer="carro"))

    await game.guess("carro")

    assert game.result == 1


@pytest.mark.asyncio
async def test_wrong_guess_returns_ongoing() -> None:
    game = Game(game_adapter=LocalAdapter(answer="carro"))
    result = await game.guess("bolas")
    assert result == 0


@pytest.mark.asyncio
async def test_six_wrong_guesses_returns_loss() -> None:
    game = Game(game_adapter=LocalAdapter(answer="carro"))
    words = ["bolas", "fundo", "pista", "milho", "torta", "gives"]
    for word in words:
        result = await game.guess(word)
    assert result == -1


@pytest.mark.asyncio
async def test_rejects_short_word() -> None:
    game = Game(game_adapter=LocalAdapter(answer="carro"))
    with pytest.raises(LengthWordError):
        await game.guess("oi")


@pytest.mark.asyncio
async def test_rejects_non_alpha() -> None:
    game = Game(game_adapter=LocalAdapter(answer="carro"))
    with pytest.raises(NotAlphaWordError):
        await game.guess("carr0")


@pytest.mark.asyncio
async def test_guess_is_recorded() -> None:
    game = Game(game_adapter=LocalAdapter(answer="carro"))
    await game.guess("bolas")
    assert "bolas" in game.guesses


@pytest.mark.asyncio
async def test_uppercase_guess_updates_remaining_letters() -> None:
    game = Game(game_adapter=LocalAdapter(answer="carro"))

    await game.guess("SALTO")

    assert not {"s", "a", "l", "t", "o"} & game.remaining
