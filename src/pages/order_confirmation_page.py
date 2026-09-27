from playwright.sync_api import Page

from src.pages.base_page import BasePage


class OrderConfirmationPage(BasePage):
    URL = "/payment_done/{order_id}"

    def __init__(self, page: Page):
        super().__init__(page)
        self.heading = page.get_by_test_id("order-placed")
        self.download_invoice_link = page.get_by_role("link", name="Download Invoice")
