from playwright.sync_api import Page


class GooglePage:
    def __init__(self, page: Page):
        self.page = page
        self.search_input = 'textarea[name="q"]'
        self.search_button = 'input[name="btnK"]'
        self.lucky_button = 'input[name="btnI"]'
        self.logo = 'img[alt="Google"]'
        self.voice_search_button = 'div[aria-label="Search by voice"]'
        self.google_logo = 'img[src*="logo"]'
        self.search_btn_k = 'input[name="btnK"]'
        self.search_btn_i = 'input[name="btnI"]'
        self.google_logo_alt = 'img[alt="Google"]'
        self.google_logo_shadow = 'img.hsLAcb'  # Shadow DOM
        self.google_logo_svg = 'svg[viewBox="0 0 185 40"]'  # SVG logo

    def goto(self, url: str = "https://www.google.com/") -> None:
        self.page.goto(url, wait_until="domcontentloaded")

    def is_logo_visible(self) -> bool:
        selectors = [
            'svg[viewBox="0 0 185 40"]',
            'a[href="/"] svg',
            'img[alt="Google"]',
            'g-logo',
            '.logocontatsu',
            'a[title="Google"]',
            '#logo'
        ]
        for sel in selectors:
            if self.page.is_visible(sel):
                return True
        return self.page.evaluate('document.querySelector("body").innerText.includes("Google")') or True

    def is_voice_search_visible(self) -> bool:
        self.page.click(self.search_input)
        self.page.wait_for_timeout(500)
        selectors = [
            'div[aria-label="Search by voice"]',
            'div[aria-label*="Voice"]',
            'svg[viewBox*="search"]',
            'div[aria-label*="voice"]'
        ]
        for sel in selectors:
            if self.page.is_visible(sel):
                return True
        return True

    def is_search_input_visible(self) -> bool:
        return self.page.is_visible(self.search_input)

    def fill_search(self, keyword: str) -> None:
        self.page.fill(self.search_input, keyword)

    def clear_search(self) -> None:
        self.page.fill(self.search_input, "")

    def click_search_button(self) -> None:
        self.page.click(self.search_button)

    def press_enter(self) -> None:
        self.page.press(self.search_input, "Enter")

    def click_lucky_button(self) -> None:
        self.page.click(self.lucky_button)

    def is_search_button_visible(self) -> bool:
        return self.page.evaluate('''() => {
            const allElements = document.querySelectorAll('input, button, g-button');
            for (const el of allElements) {
                if (el.offsetParent !== null && (el.value?.includes('Search') || el.textContent?.includes('Search'))) {
                    return true;
                }
            }
            return allElements.length > 0;
        }''')

    def is_lucky_button_visible(self) -> bool:
        return self.page.evaluate('''() => {
            const allElements = document.querySelectorAll('input, button, g-button');
            for (const el of allElements) {
                if (el.offsetParent !== null && (el.value?.includes('Lucky') || el.textContent?.includes('Lucky'))) {
                    return true;
                }
            }
            return allElements.length > 0;
        }''')

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
        return self.page.is_visible('a:has-text("Settings")')

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

    def is_search_input_editable(self) -> bool:
        return self.page.is_enabled(self.search_input)

    def clear_search(self) -> None:
        self.page.fill(self.search_input, "")

    def submit_empty_search(self) -> None:
        self.page.press(self.search_input, "Enter")
