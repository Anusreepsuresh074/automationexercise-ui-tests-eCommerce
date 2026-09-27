import allure
from playwright.sync_api import Page


class AddedToCartModal:
    """The "Added!" confirmation modal shown after adding any product to
    the cart — identical on the products grid and the product details page."""

    def __init__(self, page: Page):
        self.page = page
        self.root = page.locator(".modal-content", has_text="Added!")
        self.view_cart_link = self.root.get_by_role("link", name="View Cart")

    @allure.step("Go to cart from the confirmation modal")
    def view_cart(self) -> None:
        self.view_cart_link.click()
        self.page.wait_for_url("**/view_cart")
        # The cart's checkout button is a jQuery handler bound on load.
        self.page.wait_for_load_state("load")
