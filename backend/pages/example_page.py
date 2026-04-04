from typing import Optional
from playwright.sync_api import Page


class ExamplePage:
    def __init__(self, page: Page):
        self.page = page
        self.url = "https://example.com"

    def open(self, url: Optional[str] = None) -> None:
        target_url = url or self.url
        self.page.goto(target_url)

    def get_title(self) -> str:
        return self.page.title()

    def get_content(self) -> str:
        return self.page.content()

    def is_main_content_visible(self) -> bool:
        return self.page.is_visible("main")

    def get_images(self):
        return self.page.query_selector_all("img")

    def get_links(self):
        return self.page.query_selector_all("a")

    def get_page_load_time(self) -> float:
        start = self.page.evaluate("_ => performance.timing.navigationStart")
        self.page.wait_for_load_state("load")
        load_end = self.page.evaluate("_ => performance.timing.loadEventEnd")
        return (load_end - start) / 1000
