from playwright.sync_api import sync_playwright


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
        if self.result != 0:
            return "Lost"

        if len(word) != 5:
            return "Error"

        if not word.isalpha():
            return "Error"

        for letter in word.lower():
            self.page.click(f"[id='kbd_{letter}']")

        self.page.get_by_role("button", name="ENTER").click()

        self.guesses.append(word)
        self._update_result()
        self.word_index += 1

        return self.result

    def _update_result(self):
        word_locator = self.page.locator(
            f"[id='board0'] [termo-row='{self.word_index}']"
        )

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
