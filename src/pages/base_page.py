import allure
from playwright.sync_api import Locator, Page


class BasePage:
    """Elements shared by every page: the global header/nav. Subclasses set
    URL to their path (relative to the configured base_url)."""

    URL = "/"

    def __init__(self, page: Page):
        self.page = page
        self.header = page.locator("#header")
        self.nav_signup_login = page.locator('a[href="/login"]')
        self.nav_logout = page.locator('a[href="/logout"]')
        self.nav_delete_account = page.locator('a[href="/delete_account"]')

    def goto(self) -> None:
        with allure.step(f"Open {self.URL}"):
            self.page.goto(self.URL)

    def logged_in_as(self, name: str) -> Locator:
        return self.page.get_by_text(f"Logged in as {name}")

    @staticmethod
    def is_rejected_as_malformed(field: Locator) -> bool:
        """True when the browser's native validation flags the value as the
        wrong format (e.g. no "@" in a type="email" field). Checks the
        ValidityState rather than message text, which differs per browser."""
        return field.evaluate("el => el.validity.typeMismatch")

    @staticmethod
    def is_rejected_as_missing(field: Locator) -> bool:
        """True when the browser's native validation flags a required field as empty."""
        return field.evaluate("el => el.validity.valueMissing")
