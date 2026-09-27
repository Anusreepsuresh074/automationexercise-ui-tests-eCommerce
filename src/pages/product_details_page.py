import allure
from playwright.sync_api import Page

from src.pages.base_page import BasePage
from src.pages.components.added_to_cart_modal import AddedToCartModal


class ProductDetailsPage(BasePage):
    URL = "/product_details/{product_id}"

    def __init__(self, page: Page):
        super().__init__(page)
        info = page.locator(".product-information")
        self.name = info.get_by_role("heading", level=2)
        self.price = info.get_by_text("Rs.")
        self.quantity = page.locator("#quantity")
        self.add_to_cart_button = page.get_by_role("button", name="Add to cart")
        self.added_to_cart_modal = AddedToCartModal(page)
        self.review_name = page.locator("#name")
        self.review_email = page.locator("#email")
        self.review_text = page.locator("#review")
        self.review_submit = page.locator("#button-review")
        self.review_success = page.get_by_text("Thank you for your review.")

    @allure.step("Open product {product_id}")
    def goto(self, product_id: int) -> None:
        self.page.goto(self.URL.format(product_id=product_id))

    @allure.step("Set quantity to {quantity}")
    def set_quantity(self, quantity: str) -> None:
        self.quantity.fill(str(quantity))

    @allure.step("Type '{text}' into quantity, key by key")
    def type_quantity(self, text: str) -> None:
        """Types like a user would, unlike set_quantity()'s fill() — which
        Playwright refuses outright for non-numeric text in a number input."""
        self.quantity.press_sequentially(text)

    @allure.step("Add to cart")
    def add_to_cart(self) -> None:
        self.add_to_cart_button.click()

    @allure.step("Add product {product_id} to cart and open the cart")
    def add_to_cart_and_open_cart(self, product_id: int, quantity: str = "1") -> None:
        self.goto(product_id)
        self.set_quantity(quantity)
        self.add_to_cart()
        self.added_to_cart_modal.view_cart()

    @allure.step("Submit review as {name}")
    def submit_review(self, name: str, email: str, review: str) -> None:
        self.review_name.fill(name)
        self.review_email.fill(email)
        self.review_text.fill(review)
        self.review_submit.click()
