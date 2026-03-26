from typing import Any
from typing_extensions import Self
from playwright.sync_api import sync_playwright

from exceptions import InvalidWordError


class BoardBrowser:
    """Handles all Playwright interactions"""

    def __init__(self, headless: bool = True):
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(headless=headless)
        context = self._browser.new_context()

        self._page = context.new_page()
        self._page.goto("https://term.ooo/")
        self._page.locator("#all").click()  # click away to ignore tutorial

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args: list[Any]) -> None:
        self.close()
        return None

    def close(self) -> None:
        self._browser.close()
        self._playwright.stop()

    def input_submit_guess(self, word: str) -> None:
        for letter in word.lower():
            self._page.click(f"#kbd_{letter}")

        self._page.get_by_role("button", name="ENTER").click()

    def check_result(self, word_index: int) -> None:
        # Waits for answer animation to fisish
        self._page.wait_for_selector(
            f"#board0 [termo-row='{word_index}'] [termo-pos='4']:not(.empty)",
            timeout=10000,
        )

        self._error_notification()

    # Checks for if an error shows up on screen
    def _error_notification(self) -> None:
        notify = self._page.locator("wc-notify #msg[style*='normal']")
        if notify.is_visible():
            message = self._page.locator("wc-notify").inner_text()
            raise InvalidWordError(f"Got invalid word error message: {message}")

    def clean_guess(self) -> None:
        for _ in range(5):
            self._page.click("#kbd_backspace")

    def fetch_row_result(self, row_index: int) -> str:
        word_locator = self._page.locator(f"#board0 [termo-row='{row_index}']")
        return "".join(
            word_locator.locator(f"[termo-pos='{i}']").get_attribute("class") or ""
            for i in range(5)
        )
