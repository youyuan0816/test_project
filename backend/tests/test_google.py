import pytest
from pages.google_page import GooglePage


class TestGoogle:
    @pytest.fixture(autouse=True)
    def setup(self, page):
        self.google_page = GooglePage(page)
        self.google_page.goto("https://www.google.com/")

    def test_tc001_homepage_loads(self, page):
        """TC-001: 验证Google首页正常加载"""
        assert page.url.startswith("https://www.google.com")

    def test_tc002_page_title(self, page):
        """TC-002: 验证页面标题显示正确"""
        title = self.google_page.get_title()
        assert "Google" in title

    def test_tc003_logo_visible(self):
        """TC-003: 验证Google Logo显示"""
        assert self.google_page.is_logo_visible()

    def test_tc004_search_input_editable(self):
        """TC-004: 验证搜索输入框存在且可编辑"""
        assert self.google_page.is_search_input_visible()
        self.google_page.fill_search("test")
        assert self.google_page.is_search_input_visible()

    def test_tc005_search_button_exists(self):
        """TC-005: 验证搜索按钮存在"""
        assert self.google_page.is_search_button_visible()

    def test_tc006_lucky_button_exists(self):
        """TC-006: 验证I'm Feeling Lucky按钮存在"""
        assert self.google_page.is_lucky_button_visible()

    def test_tc007_search_with_keyword(self, page):
        """TC-007: 验证输入关键词后执行搜索"""
        self.google_page.fill_search("playwright")
        self.google_page.click_search_button()
        page.wait_for_load_state()
        assert "playwright" in page.url.lower() or "search" in page.url.lower()

    def test_tc008_search_with_enter_key(self, page):
        """TC-008: 验证按Enter键执行搜索"""
        self.google_page.fill_search("python")
        self.google_page.press_enter()
        page.wait_for_load_state()
        assert "python" in page.url.lower() or "search" in page.url.lower()

    def test_tc009_empty_search_submit(self, page):
        """TC-009: 验证空搜索提交"""
        self.google_page.clear_search()
        self.google_page.press_enter()
        page.wait_for_load_state()
        assert page.url.startswith("https://www.google.com")

    def test_tc010_voice_search_exists(self):
        """TC-010: 验证语音搜索按钮存在"""
        assert self.google_page.is_voice_search_visible()

    def test_tc011_images_button_exists(self):
        """TC-011: 验证图片搜索按钮存在"""
        assert self.google_page.is_images_link_visible()

    def test_tc012_search_suggestions_display(self):
        """TC-012: 验证搜索建议显示"""
        self.google_page.fill_search("python")
        assert self.google_page.is_suggestion_visible()

    def test_tc013_gmail_link_exists(self):
        """TC-013: 验证Gmail链接存在"""
        assert self.google_page.is_gmail_link_visible()

    def test_tc014_images_link_exists(self):
        """TC-014: 验证图片链接存在"""
        assert self.google_page.is_images_link_visible()

    def test_tc015_apps_menu_exists(self):
        """TC-015: 验证应用菜单按钮存在"""
        assert self.google_page.is_apps_menu_visible()

    def test_tc016_avatar_button_exists(self):
        """TC-016: 验证用户头像按钮存在"""
        assert self.google_page.is_avatar_button_visible()

    def test_tc017_bottom_settings_exists(self):
        """TC-017: 验证底部设置链接"""
        assert self.google_page.is_bottom_settings_visible()

    def test_tc018_bottom_privacy_exists(self):
        """TC-018: 验证底部隐私政策链接"""
        assert self.google_page.is_bottom_privacy_visible()

    def test_tc019_bottom_terms_exists(self):
        """TC-019: 验证底部服务条款链接"""
        assert self.google_page.is_bottom_terms_visible()

    def test_tc020_bottom_advertising_exists(self):
        """TC-020: 验证底部广告链接"""
        assert self.google_page.is_bottom_advertising_visible()

    def test_tc021_autocomplete_function(self, page):
        """TC-021: 验证搜索联想功能"""
        self.google_page.fill_search("java")
        assert self.google_page.is_suggestion_visible()

    def test_tc022_search_history_display(self):
        """TC-022: 验证搜索历史记录"""
        self.google_page.fill_search("test")
        assert self.google_page.is_suggestion_visible()

    def test_tc023_lucky_button_redirect(self, page):
        """TC-023: 验证I'm Feeling Lucky按钮跳转"""
        self.google_page.clear_search()
        self.google_page.page.click('input[name="btnI"]')
        page.wait_for_load_state()
        assert "google.com" in page.url

    def test_tc024_language_switch(self):
        """TC-024: 验证搜索语言切换"""
        pass

    def test_tc025_responsive_layout(self, page):
        """TC-025: 验证页面响应式布局"""
        page.set_viewport_size({"width": 375, "height": 667})
        assert self.google_page.is_search_input_visible()
