import pytest
from playwright.sync_api import expect

from src.pages.cart_page import CartPage
from src.pages.product_details_page import ProductDetailsPage
from tests.product_details.product_details_td import BLUE_TOP

PRODUCT_ID = BLUE_TOP.id


@pytest.mark.cart
@pytest.mark.smoke
@pytest.mark.sanity
@pytest.mark.regression
@pytest.mark.p0
def test_cart_empty_state(page):
    """Matrix #34: a fresh session's cart shows the empty message with a
    link back to /products."""
    cart_page = CartPage(page)
    cart_page.goto()
    expect(cart_page.empty_message).to_be_visible()
    expect(cart_page.empty_cart_products_link).to_have_attribute("href", "/products")


@pytest.mark.cart
@pytest.mark.smoke
@pytest.mark.sanity
@pytest.mark.regression
@pytest.mark.p0
def test_cart_shows_added_item(page):
    """Matrix #35: an added product appears with its name, price, quantity
    and total, plus Proceed To Checkout."""
    ProductDetailsPage(page).add_to_cart_and_open_cart(PRODUCT_ID)
    cart_page = CartPage(page)
    expect(cart_page.item_description(PRODUCT_ID)).to_contain_text(BLUE_TOP.name)
    expect(cart_page.item_price(PRODUCT_ID)).to_have_text(BLUE_TOP.price)
    expect(cart_page.item_quantity(PRODUCT_ID)).to_have_text("1")
    expect(cart_page.item_total(PRODUCT_ID)).to_have_text(BLUE_TOP.price)
    expect(cart_page.proceed_to_checkout_button).to_be_visible()


@pytest.mark.cart
@pytest.mark.regression
@pytest.mark.p1
def test_cart_quantity_is_not_editable(page):
    """Matrix #36: cart quantity is a greyed-out button, not an input —
    quantity can only be chosen on the product page. The "disabled" is a
    CSS class only (not the HTML disabled attribute), so that's what is
    asserted."""
    ProductDetailsPage(page).add_to_cart_and_open_cart(PRODUCT_ID)
    expect(CartPage(page).item_quantity(PRODUCT_ID)).to_have_class("disabled")


@pytest.mark.cart
@pytest.mark.regression
@pytest.mark.p1
def test_cart_remove_item_returns_to_empty(page):
    """Matrix #37: removing the only item returns the cart to its empty state."""
    ProductDetailsPage(page).add_to_cart_and_open_cart(PRODUCT_ID)
    cart_page = CartPage(page)
    cart_page.remove_item(PRODUCT_ID)
    expect(cart_page.item_row(PRODUCT_ID)).to_have_count(0)
    expect(cart_page.empty_message).to_be_visible()
