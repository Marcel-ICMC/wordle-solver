from types import TracebackType
from typing import Self

from playwright.async_api import Browser, Page, Playwright, async_playwright

from exceptions import GameNotFinishedError, InvalidWordError


class TermoAdapter:
    """Handles all Playwright interactions"""

    def __init__(self, page: Page, playwright: Playwright, browser: Browser) -> None:
        self._page = page
        self._playwright = playwright
        self._browser = browser
        self._word_index = 0

    @classmethod
    async def create(cls, headless: bool = True) -> Self:
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=headless)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://term.ooo/")
        await page.locator("#all").click()  # click away to ignore tutorial
        return cls(page, playwright, browser)

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.close()

    async def close(self) -> None:
        await self._browser.close()
        await self._playwright.stop()

    async def input_submit_guess(self, word: str) -> list[str]:
        for letter in word.lower():
            await self._page.click(f"#kbd_{letter}", delay=50)

        await self._page.get_by_role("button", name="ENTER").click()

        await self._wait_result()
        row_result = await self._fetch_row_result()
        self._word_index += 1

        return row_result

    async def _wait_result(self) -> None:
        # Wait for either an error on screen
        # Or the last letter on _word_index to flip it's result
        await self._page.wait_for_selector(
            f"wc-notify #msg[style*='normal'], "
            f"#board0 [termo-row='{self._word_index}'] [termo-pos='4']:not(.empty)",
            timeout=10000,
        )
        await self._error_notification()

    # Checks if an error shows up on screen
    async def _error_notification(self) -> None:
        notify = self._page.locator("wc-notify #msg[style*='normal']")
        if await notify.is_visible():
            await self._clean_guess()

            message = await self._page.locator("wc-notify").inner_text()
            raise InvalidWordError(f"Got invalid word error message: {message}")

    async def _clean_guess(self) -> None:
        for _ in range(5):
            await self._page.click("#kbd_backspace")

    async def _fetch_row_result(self) -> list[str]:
        word_locator = self._page.locator(f"#board0 [termo-row='{self._word_index}']")
        row_result = []
        for i in range(5):
            result = (
                await word_locator.locator(f"[termo-pos='{i}']").get_attribute("class")
                or ""
            )
            row_result.append(result.split()[1])
        return row_result

    async def get_answer(self) -> str:
        if self._word_index != 6:
            raise GameNotFinishedError("Can't get answer without finishing the game")

        await self._page.wait_for_selector(
            "wc-notify #msg[style*='normal']", timeout=10000
        )
        notification_text = await self._page.locator("wc-notify").inner_text()
        return notification_text.split()[-1]
