import pytest

from adapters import LocalAdapter


@pytest.mark.asyncio
async def test_correct_letter_right_position() -> None:
    adapter = LocalAdapter(answer="carro")
    await adapter.input_submit_guess("carro")
    result = await adapter.fetch_row_result(0)
    assert result == ["right", "right", "right", "right", "right"]


@pytest.mark.asyncio
async def test_correct_letter_wrong_position() -> None:
    adapter = LocalAdapter(answer="carro")
    await adapter.input_submit_guess("rroca")  # r and a are in wrong positions
    result = await adapter.fetch_row_result(0)
    assert result[0] == "place"


@pytest.mark.asyncio
async def test_correct_double_letter_position() -> None:
    adapter = LocalAdapter(answer="carro")
    await adapter.input_submit_guess("raros")
    result = await adapter.fetch_row_result(0)
    assert result == ["place", "right", "right", "place", "wrong"]


@pytest.mark.asyncio
async def test_wrong_letter() -> None:
    adapter = LocalAdapter(answer="carro")
    await adapter.input_submit_guess("bbbbb")
    result = await adapter.fetch_row_result(0)
    assert all(r == "wrong" for r in result)
