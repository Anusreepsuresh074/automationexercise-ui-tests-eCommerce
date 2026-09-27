import re

import pytest
from playwright.sync_api import expect

from src.pages.cart_page import CartPage
from src.pages.product_details_page import ProductDetailsPage
from tests.product_details import product_details_td as td

PRODUCT_ID = td.BLUE_TOP.id


@pytest.mark.product_details
@pytest.mark.smoke
@pytest.mark.sanity
@pytest.mark.regression
@pytest.mark.p0
def test_product_details_renders(page):
    """Matrix #27: the product page shows name, price, quantity and Add to cart."""
    details_page = ProductDetailsPage(page)
    details_page.goto(PRODUCT_ID)
    expect(details_page.name).to_have_text(td.BLUE_TOP.name)
    expect(details_page.price).to_have_text(td.BLUE_TOP.price)
    expect(details_page.quantity).to_have_value("1")
    expect(details_page.add_to_cart_button).to_be_visible()


@pytest.mark.product_details
@pytest.mark.regression
@pytest.mark.p1
def test_product_details_quantity_large_value(page):
    """Matrix #29: a large quantity (100) reaches the cart unchanged."""
    ProductDetailsPage(page).add_to_cart_and_open_cart(PRODUCT_ID, quantity=td.LARGE_QUANTITY)
    expect(CartPage(page).item_quantity(PRODUCT_ID)).to_have_text(td.LARGE_QUANTITY)


@pytest.mark.product_details
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.xfail(
    reason='Site defect: the quantity field declares min="1", but a quantity of 0 is accepted '
    "and added to the cart as a 0-quantity line.",
    strict=True,
)
def test_product_details_quantity_below_minimum_rejected(page):
    """Matrix #28: a quantity of 0 should not be added to the cart."""
    ProductDetailsPage(page).add_to_cart_and_open_cart(PRODUCT_ID, quantity=td.BELOW_MINIMUM_QUANTITY)
    expect(CartPage(page).item_row(PRODUCT_ID)).to_have_count(0, timeout=3000)


@pytest.mark.product_details
@pytest.mark.regression
@pytest.mark.p1
def test_product_details_quantity_non_numeric_input(page):
    """Matrix #30: the quantity field is type="number", so typed letters
    never become part of its value — however the browser handles the
    keystrokes (Chromium drops them; Firefox shows them but reports an
    empty value)."""
    details_page = ProductDetailsPage(page)
    details_page.goto(PRODUCT_ID)
    expect(details_page.quantity).to_have_attribute("type", "number")
    details_page.type_quantity(td.NON_NUMERIC_QUANTITY)
    expect(details_page.quantity).not_to_have_value(re.compile(r"[^\d]"))


@pytest.mark.product_details
@pytest.mark.regression
@pytest.mark.p1
def test_product_review_submit_valid(page):
    """Matrix #31: a complete review shows "Thank you for your review."."""
    details_page = ProductDetailsPage(page)
    details_page.goto(PRODUCT_ID)
    details_page.submit_review(**td.VALID_REVIEW)
    expect(details_page.review_success).to_be_visible()


@pytest.mark.product_details
@pytest.mark.regression
@pytest.mark.p1
def test_product_review_empty_field(page):
    """Matrix #32: all review fields are required — the browser blocks an
    empty submission."""
    details_page = ProductDetailsPage(page)
    details_page.goto(PRODUCT_ID)
    details_page.submit_review("", "", "")
    assert details_page.is_rejected_as_missing(details_page.review_name)
    expect(details_page.review_success).to_be_hidden()


@pytest.mark.product_details
@pytest.mark.regression
@pytest.mark.p1
def test_product_review_invalid_email_format(page):
    """Matrix #33: the review email field rejects a malformed address."""
    details_page = ProductDetailsPage(page)
    details_page.goto(PRODUCT_ID)
    details_page.submit_review(td.VALID_REVIEW["name"], td.MALFORMED_EMAIL, td.VALID_REVIEW["review"])
    assert details_page.is_rejected_as_malformed(details_page.review_email)
    expect(details_page.review_success).to_be_hidden()
