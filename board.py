from playwright.sync_api import sync_playwright

from exceptions import InvalidWordError, LengthWordlError, NotAlphaWordError
from utils import strip_accents


class Board:
    def __init__(self, headless=True):
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(headless=headless)
        context = browser.new_context()

        self.page = context.new_page()
        self.page.goto("https://term.ooo/")
        self.page.locator("#all").click()  # click away to ignore tutorial

        self.word_index = 0
        self.guesses = []
        self.results = []
        self.result = 0

    def guess(self, word):
        if len(word) != 5:
            raise LengthWordlError(f"Word should be exactly 5 characters, not {word}")

        if not word.isalpha():
            raise NotAlphaWordError(
                f"Word should contain only alphabetical characters, not {word}"
            )

        self._input_submit_guess(strip_accents(word))
        self._check_result()
        self._update_result()

        self.guesses.append(word)
        self.word_index += 1

        return self.result

    def _update_result(self):
        word_locator = self.page.locator(f"#board0 [termo-row='{self.word_index}']")
        word_result = []
        for l in range(5):
            letter = (
                word_locator.locator(f"[termo-pos='{l}']")
                .get_attribute("class")
                .split()[1]
            )
            word_result.append(letter)

        self.results.append(word_result)

        if all(r == "right" for r in self.results[-1]):
            self.result = 1
        if len(self.results) == 6:
            self.result = -1

    def _check_result(self):
        # Waits for answer animation to fisish
        self.page.wait_for_selector(
            f"#board0 [termo-row='{self.word_index}'] [termo-pos='4']:not(.empty)",
            timeout=10000,
        )

        try:
            self._error_notification()
        except InvalidWordError:
            print("Invalid word")
            self._clean_guess()

    # Checks for if an error shows up on screen
    def _error_notification(self):
        notify = self.page.locator("wc-notify #msg[style*='normal']")
        if notify.is_visible():
            message = self.page.locator("wc-notify").inner_text()
            raise InvalidWordError(f"Got invalid word error message: {message}")

    def _input_submit_guess(self, word):
        for letter in word.lower():
            self.page.click(f"#kbd_{letter}")

        self.page.get_by_role("button", name="ENTER").click()

    def _clean_guess(self):
        for _ in range(5):
            self.page.click(f"#kbd_backspace")
