import allure
from playwright.sync_api import Locator, Page

from src.pages.base_page import BasePage
from src.pages.components.added_to_cart_modal import AddedToCartModal


class ProductsPage(BasePage):
    URL = "/products"

    def __init__(self, page: Page):
        super().__init__(page)
        self.search_input = page.locator("#search_product")
        self.search_button = page.locator("#submit_search")
        self.product_cards = page.locator(".product-image-wrapper")
        self.searched_products_heading = page.get_by_role("heading", name="Searched Products")
        self.added_to_cart_modal = AddedToCartModal(page)

    def listing_heading(self, text: str) -> Locator:
        return self.page.get_by_role("heading", name=text)

    @allure.step("Search products for '{term}'")
    def search(self, term: str) -> None:
        self.search_input.fill(term)
        self.search_button.click()

    @allure.step("Filter by category {category_href}")
    def filter_by_category(self, parent_toggle_href: str, category_href: str) -> None:
        # Sub-categories sit in a collapsed Bootstrap accordion panel — the
        # parent toggle has to be expanded before the link is clickable.
        self.page.locator(f'a[href="{parent_toggle_href}"]').click()
        link = self.page.locator(f'a[href="{category_href}"]')
        link.click()
        self.page.wait_for_url(f"**{category_href}")

    @allure.step("Filter by brand {brand_name}")
    def filter_by_brand(self, brand_name: str) -> None:
        self.page.locator(f'a[href="/brand_products/{brand_name}"]').click()
        self.page.wait_for_url(f"**/brand_products/{brand_name}")

    @allure.step("Add product {product_id} to cart from the grid")
    def add_to_cart(self, product_id: int) -> None:
        self.page.locator(f'a.add-to-cart[data-product-id="{product_id}"]').first.click()

    def search_input_is_focused(self) -> bool:
        return self.search_input.evaluate("el => el === document.activeElement")
