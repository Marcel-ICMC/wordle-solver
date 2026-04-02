from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio

from adapters import LocalAdapter, TermoAdapter

VALID_WORDS = ["carro", "bolas", "fundo", "pista", "milho", "torta"]


@pytest_asyncio.fixture
async def adapter() -> AsyncGenerator[TermoAdapter, None]:
    async with await TermoAdapter.create(headless=True) as adapter:
        yield adapter


async def test_page_loads(adapter: TermoAdapter) -> None:
    assert await adapter._page.locator("#board0").is_visible()


async def test_correct_guess_returns_all_right(
    adapter: TermoAdapter, answer: str
) -> None:
    result = await adapter.input_submit_guess(answer)
    assert all(r == "right" for r in result)


async def test_known_letter_returns_place(
    adapter: TermoAdapter, answer: str, request: pytest.FixtureRequest
) -> None:
    for word in VALID_WORDS:
        for wrong_pos, letter in enumerate(word):
            if letter in answer and answer[wrong_pos] != letter:
                result = await adapter.input_submit_guess(word)
                assert result[wrong_pos] == "place"
                return

    pytest.skip(
        f"{request.node.name}: could not construct a place scenario for answer '{answer}'"
    )


async def test_wrong_letters_return_wrong(
    adapter: TermoAdapter, answer: str, request: pytest.FixtureRequest
) -> None:
    for word in VALID_WORDS:
        for wrong_letter_pos, wrong_letter in enumerate(word):
            if wrong_letter not in answer:
                result = await adapter.input_submit_guess(word)
                assert result[wrong_letter_pos] == "wrong"
                return

    pytest.skip(
        f"{request.node.name}: could not construct a place scenario for answer '{answer}'"
    )


async def test_local_and_termo_agree(adapter: TermoAdapter, answer: str) -> None:
    local = LocalAdapter(answer=answer)

    guess = "carro"
    termo_result = await adapter.input_submit_guess(guess)
    local_result = await local.input_submit_guess(guess)

    assert termo_result == local_result
