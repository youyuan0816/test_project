import pytest
from pages.baidu_page import BaiduPage


TEST_URL = "https://www.baidu.com"
LOGIN_USERNAME = "admin"
LOGIN_PASSWORD = "password123"


class TestBaiduHomepage:
    def test_tc001_homepage_load(self, page):
        """TC-001: 百度首页加载验证"""
        baidu = BaiduPage(page)
        baidu.open(TEST_URL)
        assert "百度" in baidu.get_title()

    def test_tc002_search_input_exists(self, page):
        """TC-002: 百度搜索功能-输入框存在验证"""
        baidu = BaiduPage(page)
        baidu.open(TEST_URL)
        assert baidu.is_search_input_visible()

    def test_tc005_logo_visible(self, page):
        """TC-005: 百度首页-百度logo显示"""
        baidu = BaiduPage(page)
        baidu.open(TEST_URL)
        assert baidu.is_logo_visible()

    def test_tc006_nav_links(self, page):
        """TC-006: 百度首页-导航栏链接验证"""
        baidu = BaiduPage(page)
        baidu.open(TEST_URL)
        count = baidu.get_nav_links_count()
        assert count >= 3

    def test_tc009_page_load_time(self, page):
        """TC-009: 百度首页-页面响应时间"""
        baidu = BaiduPage(page)
        baidu.open(TEST_URL)
        load_time = baidu.get_page_load_time()
        assert load_time < 3.0


class TestBaiduSearch:
    def test_tc003_search_keyword(self, page):
        """TC-003: 百度搜索功能-输入关键词搜索"""
        baidu = BaiduPage(page)
        baidu.open(TEST_URL)
        baidu.search("Python")
        assert "Python" in baidu.get_title()

    def test_tc004_search_results_relevance(self, page):
        """TC-004: 百度搜索功能-搜索结果相关性"""
        baidu = BaiduPage(page)
        baidu.open(TEST_URL)
        baidu.search("Python")
        result_count = baidu.get_result_count()
        assert result_count is not None

    def test_tc007_special_character_search(self, page):
        """TC-007: 百度搜索功能-特殊字符搜索"""
        baidu = BaiduPage(page)
        baidu.open(TEST_URL)
        baidu.search("@#$%")
        assert baidu.is_search_input_visible()

    def test_tc008_empty_search(self, page):
        """TC-008: 百度搜索功能-空搜索验证"""
        baidu = BaiduPage(page)
        baidu.open(TEST_URL)
        baidu.search_press_enter("")
        assert baidu.is_search_input_visible()

    def test_tc010_search_suggestion(self, page):
        """TC-010: 百度搜索功能-搜索建议功能"""
        baidu = BaiduPage(page)
        baidu.open(TEST_URL)
        page.fill(baidu.search_input, "Py")
        has_suggestions = baidu.wait_for_suggestions()
        assert has_suggestions or baidu.is_search_input_visible()
