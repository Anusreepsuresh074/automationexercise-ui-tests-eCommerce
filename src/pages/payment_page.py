import allure
from playwright.sync_api import Page

from src.pages.base_page import BasePage


class PaymentPage(BasePage):
    URL = "/payment"

    def __init__(self, page: Page):
        super().__init__(page)
        self.name_on_card = page.get_by_test_id("name-on-card")
        self.card_number = page.get_by_test_id("card-number")
        self.cvc = page.get_by_test_id("cvc")
        self.expiry_month = page.get_by_test_id("expiry-month")
        self.expiry_year = page.get_by_test_id("expiry-year")
        self.pay_button = page.get_by_test_id("pay-button")

    @allure.step("Pay with card")
    def pay_with_card(
        self, *, name_on_card: str, card_number: str, cvc: str, expiry_month: str, expiry_year: str
    ) -> None:
        self.name_on_card.fill(name_on_card)
        self.card_number.fill(card_number)
        self.cvc.fill(cvc)
        self.expiry_month.fill(expiry_month)
        self.expiry_year.fill(expiry_year)
        self.pay_button.click()
