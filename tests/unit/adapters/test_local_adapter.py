import pytest

from adapters import LocalAdapter


@pytest.mark.asyncio
async def test_correct_letter_right_position() -> None:
    adapter = LocalAdapter(answer="carro")
    result = await adapter.input_submit_guess("carro")
    assert result == ["right", "right", "right", "right", "right"]


@pytest.mark.asyncio
async def test_correct_letter_wrong_position() -> None:
    adapter = LocalAdapter(answer="carro")
    result = await adapter.input_submit_guess("rroca")  # r and a are in wrong positions
    assert result[0] == "place"


@pytest.mark.asyncio
async def test_correct_double_letter_position() -> None:
    adapter = LocalAdapter(answer="carro")
    result = await adapter.input_submit_guess("raros")
    assert result == ["place", "right", "right", "place", "wrong"]


@pytest.mark.asyncio
async def test_wrong_letter() -> None:
    adapter = LocalAdapter(answer="carro")
    result = await adapter.input_submit_guess("bbbbb")
    assert all(r == "wrong" for r in result)
