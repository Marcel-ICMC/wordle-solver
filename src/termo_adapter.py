from typing import Any, Self

from playwright.async_api import Browser, Page, Playwright, async_playwright

from exceptions import InvalidWordError


class TermoAdapter:
    """Handles all Playwright interactions"""

    def __init__(self, page: Page, playwright: Playwright, browser: Browser) -> None:
        self._page = page
        self._playwright = playwright
        self._browser = browser

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

    async def __aexit__(self, *args: list[Any]) -> None:
        await self.close()
        return None

    async def close(self) -> None:
        await self._browser.close()
        await self._playwright.stop()

    async def input_submit_guess(self, word: str) -> None:
        for letter in word.lower():
            await self._page.click(f"#kbd_{letter}")

        await self._page.get_by_role("button", name="ENTER").click()

    async def check_result(self, word_index: int) -> None:
        # Waits for answer animation to fisish
        await self._page.wait_for_selector(
            f"#board0 [termo-row='{word_index}'] [termo-pos='4']:not(.empty)",
            timeout=10000,
        )

        await self._error_notification()

    # Checks if an error shows up on screen
    async def _error_notification(self) -> None:
        notify = self._page.locator("wc-notify #msg[style*='normal']")
        if await notify.is_visible():
            message = await self._page.locator("wc-notify").inner_text()
            raise InvalidWordError(f"Got invalid word error message: {message}")

    async def clean_guess(self) -> None:
        for _ in range(5):
            await self._page.click("#kbd_backspace")

    async def fetch_row_result(self, row_index: int) -> list[str]:
        word_locator = self._page.locator(f"#board0 [termo-row='{row_index}']")
        row_result = []
        for i in range(5):
            result = (
                await word_locator.locator(f"[termo-pos='{i}']").get_attribute("class")
                or ""
            )
            row_result.append(result.split()[1])
        return row_result
