from playwright.sync_api import Page


class GooglePage:
    def __init__(self, page: Page):
        self.page = page
        self.search_input = 'textarea[name="q"]'
        self.search_button = 'input[name="btnK"]'
        self.lucky_button = 'input[name="btnI"]'
        self.logo = 'img[alt="Google"]'
        self.voice_search_button = 'div[aria-label="Search by voice"]'

    def goto(self, url: str = "https://www.google.com/") -> None:
        self.page.goto(url)

    def is_logo_visible(self) -> bool:
        return self.page.is_visible(self.logo)

    def is_search_input_visible(self) -> bool:
        return self.page.is_visible(self.search_input)

    def is_search_button_visible(self) -> bool:
        return self.page.is_visible(self.search_button)

    def is_lucky_button_visible(self) -> bool:
        return self.page.is_visible(self.lucky_button)

    def is_voice_search_visible(self) -> bool:
        return self.page.is_visible(self.voice_search_button)

    def fill_search(self, keyword: str) -> None:
        self.page.fill(self.search_input, keyword)

    def clear_search(self) -> None:
        self.page.fill(self.search_input, "")

    def click_search_button(self) -> None:
        self.page.click(self.search_button)

    def press_enter(self) -> None:
        self.page.press(self.search_input, "Enter")

    def get_title(self) -> str:
        return self.page.title()

    def is_images_link_visible(self) -> bool:
        return self.page.is_visible('a:has-text("Images")')

    def is_gmail_link_visible(self) -> bool:
        return self.page.is_visible('a:has-text("Gmail")')

    def is_apps_menu_visible(self) -> bool:
        return self.page.is_visible('div[aria-label="Google apps"]')

    def is_avatar_button_visible(self) -> bool:
        return self.page.is_visible('#gb > div > div > a')

    def is_bottom_settings_visible(self) -> bool:
        return self.page.is_visible('#bottom_text > a')

    def is_bottom_privacy_visible(self) -> bool:
        return self.page.is_visible('a:has-text("Privacy")')

    def is_bottom_terms_visible(self) -> bool:
        return self.page.is_visible('a:has-text("Terms")')

    def is_bottom_advertising_visible(self) -> bool:
        return self.page.is_visible('a:has-text("Advertising")')

    def get_suggestions(self) -> list:
        return self.page.query_selector_all('ul[role="listbox"] li')

    def is_suggestion_visible(self) -> bool:
        return self.page.is_visible('ul[role="listbox"]')

    def is_images_link_visible(self) -> bool:
        return self.page.is_visible('a:has-text("Images")')

    def is_gmail_link_visible(self) -> bool:
        return self.page.is_visible('a:has-text("Gmail")')

    def is_apps_menu_visible(self) -> bool:
        return self.page.is_visible('div[aria-label="Google apps"]')

    def is_avatar_button_visible(self) -> bool:
        return self.page.is_visible('#gb > div > div > a')

    def is_bottom_settings_visible(self) -> bool:
        return self.page.is_visible('a:has-text("Settings")')

    def is_bottom_privacy_visible(self) -> bool:
        return self.page.is_visible('a:has-text("Privacy")')

    def is_bottom_terms_visible(self) -> bool:
        return self.page.is_visible('a:has-text("Terms")')

    def is_bottom_advertising_visible(self) -> bool:
        return self.page.is_visible('a:has-text("Advertising")')
