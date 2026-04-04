import pytest
from pages.example_page import ExamplePage


TEST_URL = "https://example.com"
LOGIN_USERNAME = ""
LOGIN_PASSWORD = ""


class TestExamplePage:
    def test_tc001_page_load(self, page):
        """TC-001: Example页面加载验证"""
        example = ExamplePage(page)
        example.open(TEST_URL)
        assert example.get_title() is not None

    def test_tc002_title_verification(self, page):
        """TC-002: Example页面标题验证"""
        example = ExamplePage(page)
        example.open(TEST_URL)
        title = example.get_title()
        assert title is not None and len(title) > 0

    def test_tc003_content_verification(self, page):
        """TC-003: Example页面内容验证"""
        example = ExamplePage(page)
        example.open(TEST_URL)
        content = example.get_content()
        assert content is not None and len(content) > 0

    def test_tc004_image_verification(self, page):
        """TC-004: Example页面图片验证"""
        example = ExamplePage(page)
        example.open(TEST_URL)
        images = example.get_images()
        assert images is not None

    def test_tc005_link_verification(self, page):
        """TC-005: Example页面链接验证"""
        example = ExamplePage(page)
        example.open(TEST_URL)
        links = example.get_links()
        assert links is not None and len(links) > 0

    def test_tc006_page_load_time(self, page):
        """TC-006: Example页面响应时间"""
        example = ExamplePage(page)
        example.open(TEST_URL)
        load_time = example.get_page_load_time()
        assert load_time > 0

    def test_tc007_compatibility(self, page):
        """TC-007: Example页面兼容性"""
        example = ExamplePage(page)
        example.open(TEST_URL)
        title = example.get_title()
        content = example.get_content()
        assert title is not None and content is not None
