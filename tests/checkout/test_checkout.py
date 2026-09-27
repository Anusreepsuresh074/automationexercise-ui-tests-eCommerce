import re

import pytest
from playwright.sync_api import expect

from src.pages.cart_page import CartPage
from src.pages.checkout_page import CheckoutPage
from src.pages.login_page import LoginPage
from src.pages.order_confirmation_page import OrderConfirmationPage
from src.pages.payment_page import PaymentPage
from src.pages.product_details_page import ProductDetailsPage
from tests.checkout import checkout_td
from tests.product_details.product_details_td import BLUE_TOP

PRODUCT_ID = BLUE_TOP.id


def _checkout_to_payment(page) -> PaymentPage:
    ProductDetailsPage(page).add_to_cart_and_open_cart(PRODUCT_ID)
    CartPage(page).proceed_to_checkout()
    CheckoutPage(page).place_order()
    return PaymentPage(page)


@pytest.mark.checkout
@pytest.mark.regression
@pytest.mark.p1
def test_checkout_requires_login(page):
    """Matrix #38: a logged-out user who proceeds to checkout is asked to
    register / log in instead of reaching /checkout."""
    ProductDetailsPage(page).add_to_cart_and_open_cart(PRODUCT_ID)
    cart_page = CartPage(page)
    cart_page.proceed_to_checkout()
    expect(cart_page.checkout_login_prompt).to_be_visible()
    expect(cart_page.checkout_login_prompt_link).to_have_attribute("href", LoginPage.URL)
    expect(page).to_have_url(re.compile(rf"{CartPage.URL}$"))


@pytest.mark.checkout
@pytest.mark.smoke
@pytest.mark.sanity
@pytest.mark.regression
@pytest.mark.p0
def test_checkout_happy_path(authenticated_page):
    """Matrix #39: end-to-end purchase — cart → checkout (address and order
    review shown) → payment → "Order Placed!" with an invoice link."""
    page = authenticated_page
    ProductDetailsPage(page).add_to_cart_and_open_cart(PRODUCT_ID)
    CartPage(page).proceed_to_checkout()

    checkout_page = CheckoutPage(page)
    expect(checkout_page.delivery_address).to_be_visible()
    expect(checkout_page.order_review).to_contain_text(BLUE_TOP.name)
    checkout_page.add_order_comment(checkout_td.ORDER_COMMENT)
    checkout_page.place_order()

    PaymentPage(page).pay_with_card(**checkout_td.VALID_CARD)

    confirmation_page = OrderConfirmationPage(page)
    expect(confirmation_page.heading).to_be_visible()
    expect(confirmation_page.download_invoice_link).to_have_attribute("href", re.compile(r"^/download_invoice/\d+$"))


@pytest.mark.checkout
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.xfail(
    reason="Site defect: the payment form accepts a non-numeric card number (abcd1234) and places the order.",
    strict=True,
)
def test_checkout_invalid_payment_details_rejected(authenticated_page):
    """Matrix #40: a card number containing letters should be rejected."""
    page = authenticated_page
    _checkout_to_payment(page).pay_with_card(**checkout_td.NON_NUMERIC_CARD)
    page.wait_for_load_state("load")  # let an accepted payment finish navigating
    expect(page).to_have_url(re.compile(rf"{PaymentPage.URL}$"), timeout=2000)
