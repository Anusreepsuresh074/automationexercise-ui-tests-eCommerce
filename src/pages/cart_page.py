import allure
from playwright.sync_api import Locator, Page

from src.pages.base_page import BasePage


class CartPage(BasePage):
    URL = "/view_cart"

    def __init__(self, page: Page):
        super().__init__(page)
        self.empty_message = page.get_by_text("Cart is empty! Click here to buy products.")
        self.empty_cart_products_link = page.locator("#empty_cart a")
        # Not a real link: a jQuery click handler bound on page load. Logged
        # in it goes to /checkout; logged out it opens checkout_login_prompt.
        self.proceed_to_checkout_button = page.get_by_text("Proceed To Checkout")
        self.checkout_login_prompt = page.locator("#checkoutModal")
        self.checkout_login_prompt_link = self.checkout_login_prompt.get_by_role("link", name="Register / Login")

    def item_row(self, product_id: int) -> Locator:
        return self.page.locator(f"#product-{product_id}")

    def item_description(self, product_id: int) -> Locator:
        return self.item_row(product_id).locator(".cart_description")

    def item_price(self, product_id: int) -> Locator:
        return self.item_row(product_id).locator(".cart_price")

    def item_quantity(self, product_id: int) -> Locator:
        return self.item_row(product_id).locator(".cart_quantity button")

    def item_total(self, product_id: int) -> Locator:
        return self.item_row(product_id).locator(".cart_total")

    @allure.step("Remove product {product_id} from cart")
    def remove_item(self, product_id: int) -> None:
        self.item_row(product_id).locator("a.cart_quantity_delete").click()

    @allure.step("Proceed to checkout")
    def proceed_to_checkout(self) -> None:
        # Clicking before the handler is bound silently does nothing (seen on Firefox).
        self.page.wait_for_load_state("load")
        self.proceed_to_checkout_button.click()
