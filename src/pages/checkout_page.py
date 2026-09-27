import allure
from playwright.sync_api import Page

from src.pages.base_page import BasePage


class CheckoutPage(BasePage):
    URL = "/checkout"

    def __init__(self, page: Page):
        super().__init__(page)
        self.delivery_address = page.locator("#address_delivery")
        self.order_review = page.locator("#cart_info")
        self.order_comment = page.locator('textarea[name="message"]')
        self.place_order_button = page.get_by_role("link", name="Place Order")

    @allure.step("Add order comment")
    def add_order_comment(self, text: str) -> None:
        self.order_comment.fill(text)

    @allure.step("Place order")
    def place_order(self) -> None:
        self.place_order_button.click()
        self.page.wait_for_url("**/payment")
