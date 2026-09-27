import allure
from playwright.sync_api import Page

from src.pages.base_page import BasePage


class AccountDeletedPage(BasePage):
    """/delete_account deletes the logged-in account as soon as it loads —
    there is no confirmation step."""

    URL = "/delete_account"

    def __init__(self, page: Page):
        super().__init__(page)
        self.heading = page.get_by_test_id("account-deleted")
        self.confirmation_text = page.get_by_text("Your account has been permanently deleted!")

    @allure.step("Delete the logged-in account")
    def delete_account(self) -> None:
        """Just opening the page deletes the account — named for what it does."""
        self.goto()
