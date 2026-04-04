# AGENTS.md - Agentic Coding Guidelines

This project is a Python UI automation testing framework using Playwright and pytest.

## Commands

### Install Dependencies
```bash
pip install -r requirements.txt
playwright install chromium
```

### Run Tests
```bash
# Run all tests
pytest

# Run a specific test file
pytest tests/test_example.py

# Run a single test (recommended pattern)
pytest tests/test_example.py::test_example -v

# Run with headed browser (debug mode)
pytest --headed
```

### Other
```bash
# Run with specific browser
pytest --browser=chromium
```

## Code Style Guidelines

### Imports
- Standard library imports first
- Third-party imports second
- Local imports third
- Separate each group with a blank line
- Use absolute imports
- Example:
  ```python
  import sys
  import json

  import requests
  import pytest
  from playwright.sync_api import sync_playwright

  from pages.example_page import ExamplePage
  ```

### Formatting
- Use 4 spaces for indentation (no tabs)
- Maximum line length: 100 characters
- Use blank lines to separate logical sections (max 2 consecutive)
- Use type hints for function arguments and return values
- Example:
  ```python
  def login(page: Page, username: str, password: str) -> bool:
      page.fill("#username", username)
      page.click("#login-btn")
      return page.is_visible("#dashboard")
  ```

### Naming Conventions
- **Variables**: snake_case (e.g., `test_url`, `page_context`)
- **Functions**: snake_case (e.g., `get_element`, `fill_form`)
- **Classes**: PascalCase (e.g., `LoginPage`, `TestExample`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `DEFAULT_TIMEOUT`, `API_BASE_URL`)
- **Test functions**: test_<description> (e.g., `test_login_success`)
- **Test classes**: Test<Description> (e.g., `TestLogin`, `TestDashboard`)

### Types
- Use type hints for all function parameters and return values
- Use built-in types (str, int, bool, list, dict, etc.)
- Use Optional for nullable types:
  ```python
  def get_title(page: Page) -> Optional[str]:
  ```
- Use Union for multiple types:
  ```python
  def parse_result(data: Union[str, dict]) -> dict:
  ```

### Error Handling
- Use specific exception types
- Catch exceptions at the appropriate level
- Provide meaningful error messages
- Use try/except blocks sparingly and locally
- Example:
  ```python
  try:
      response = requests.get(url, timeout=10)
      response.raise_for_status()
  except requests.exceptions.ConnectionError:
      print("错误：无法连接到服务器")
      sys.exit(1)
  except requests.exceptions.RequestException as e:
      print(f"错误：{e}")
      sys.exit(1)
  ```

### Test Structure
- One test file per feature/module
- Use descriptive test names
- Use docstrings to explain test purpose
- Group related tests in classes
- Use fixtures for setup/teardown
- Example:
  ```python
  class TestLogin:
      def test_login_success(self, page):
          """测试登录成功场景"""
          page.goto("/login")
          page.fill("#username", "admin")
          page.fill("#password", "password")
          page.click("#submit")
          assert page.is_visible("#dashboard")
  ```

### Page Object Model
- Create page objects for each page/component
- Encapsulate locators and actions
- Keep page objects focused and single-responsibility
- Example:
  ```python
  class LoginPage:
      def __init__(self, page: Page):
          self.page = page
          self.username_input = "#username"
          self.password_input = "#password"
          self.submit_btn = "#submit"

      def login(self, username: str, password: str):
          self.page.fill(self.username_input, username)
          self.page.fill(self.password_input, password)
          self.page.click(self.submit_btn)
  ```

### Fixtures (conftest.py)
- Use session scope for browser fixture (shared across tests)
- Use function scope for page fixture (new page per test)
- Clean up resources in teardown
- Example:
  ```python
  @pytest.fixture(scope="session")
  def browser():
      with sync_playwright() as p:
          browser = p.chromium.launch()
          yield browser
          browser.close()

  @pytest.fixture(scope="function")
  def page(browser):
      context = browser.new_context()
      page = context.new_page()
      yield page
      context.close()
  ```

### Best Practices
- Use explicit waits instead of sleep
- Use CSS/XPath selectors that are stable
- Avoid hardcoded waits
- Keep tests independent (no shared state)
- Use meaningful assertions
- Clean up test data after tests
- Take screenshots on test failure for debugging

### Linting
No formal linting configured. Follow PEP 8 guidelines manually.

### Type Checking
No formal type checking configured. Ensure type hints are consistent.