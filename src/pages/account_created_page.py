import allure
from playwright.sync_api import Page

from src.pages.base_page import BasePage


class AccountCreatedPage(BasePage):
    URL = "/account_created"

    def __init__(self, page: Page):
        super().__init__(page)
        self.heading = page.get_by_test_id("account-created")
        self.continue_button = page.get_by_test_id("continue-button")

    @allure.step("Continue to home page")
    def continue_to_home(self) -> None:
        self.continue_button.click()
        self.page.wait_for_url("**/")
