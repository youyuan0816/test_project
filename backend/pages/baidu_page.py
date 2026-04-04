from typing import Optional
from playwright.sync_api import Page


class BaiduPage:
    def __init__(self, page: Page):
        self.page = page
        self.search_input = "#kw"
        self.search_button = "#su"
        self.logo = "#lg"
        self.nav_links = "#s_top_tab a"
        self.suggestion_box = ".sugcont"
        self.result_stats = "#result_num"

    def open(self, url: str) -> None:
        self.page.goto(url)

    def search(self, keyword: str) -> None:
        self.page.fill(self.search_input, keyword)
        self.page.click(self.search_button)
        self.page.wait_for_load_state("networkidle")

    def search_press_enter(self, keyword: str) -> None:
        self.page.fill(self.search_input, keyword)
        self.page.press(self.search_input, "Enter")
        self.page.wait_for_load_state("networkidle")

    def get_title(self) -> str:
        return self.page.title()

    def is_logo_visible(self) -> bool:
        return self.page.is_visible(self.logo)

    def is_search_input_visible(self) -> bool:
        return self.page.is_visible(self.search_input)

    def get_result_count(self) -> Optional[str]:
        return self.page.text_content(self.result_stats)

    def get_nav_links_count(self) -> int:
        return self.page.locator(self.nav_links).count()

    def get_page_load_time(self) -> float:
        self.page.evaluate("_ => { performance.clearResourceTimings() }")
        start = self.page.evaluate("_ => performance.timing.navigationStart")
        load_end = self.page.evaluate("_ => performance.timing.loadEventEnd")
        return (load_end - start) / 1000

    def wait_for_suggestions(self) -> bool:
        return self.page.wait_for_selector(self.suggestion_box, timeout=5000)
