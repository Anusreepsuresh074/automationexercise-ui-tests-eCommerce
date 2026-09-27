import pytest
from playwright.sync_api import expect

from src.pages.products_page import ProductsPage
from tests.products import products_td


@pytest.mark.products
@pytest.mark.smoke
@pytest.mark.sanity
@pytest.mark.regression
@pytest.mark.p0
def test_products_grid_renders(page):
    """Matrix #18, #25: the products page shows the product grid and search
    box. #25 (cross-browser parity) is covered by this same test running
    on Chromium, Firefox and WebKit in the nightly CI matrix."""
    products_page = ProductsPage(page)
    products_page.goto()
    expect(products_page.product_cards.first).to_be_visible()
    expect(products_page.search_input).to_be_visible()


@pytest.mark.products
@pytest.mark.regression
@pytest.mark.p1
def test_products_search_matching_term(page):
    """Matrix #19: searching a known term shows "Searched Products" with
    matching results."""
    products_page = ProductsPage(page)
    products_page.goto()
    products_page.search(products_td.MATCHING_SEARCH_TERM)
    expect(products_page.searched_products_heading).to_be_visible()
    expect(products_page.product_cards.first).to_be_visible()


@pytest.mark.products
@pytest.mark.regression
@pytest.mark.p1
def test_products_search_no_results(page):
    """Matrix #20: a search with no matches shows the heading and zero
    products (the site has no dedicated "no results" message)."""
    products_page = ProductsPage(page)
    products_page.goto()
    products_page.search(products_td.NO_RESULTS_SEARCH_TERM)
    expect(products_page.searched_products_heading).to_be_visible()
    expect(products_page.product_cards).to_have_count(0)


@pytest.mark.products
@pytest.mark.regression
@pytest.mark.p1
def test_products_search_special_characters_handled_safely(page):
    """Matrix #21: a script-injection string in search is treated as plain
    text — no script runs and results still render."""
    dialogs = []

    def on_dialog(dialog):
        dialogs.append(dialog.message)
        dialog.dismiss()

    page.on("dialog", on_dialog)
    try:
        products_page = ProductsPage(page)
        products_page.goto()
        products_page.search(products_td.SCRIPT_INJECTION_SEARCH_TERM)
        expect(products_page.searched_products_heading).to_be_visible()
    finally:
        page.remove_listener("dialog", on_dialog)
    assert dialogs == [], f"injected script executed: {dialogs}"


@pytest.mark.products
@pytest.mark.regression
@pytest.mark.p1
def test_products_category_filter(page):
    """Matrix #22: Women → Dress opens the filtered "Dress Products" list."""
    category = products_td.CATEGORY_WOMEN_DRESS
    products_page = ProductsPage(page)
    products_page.goto()
    products_page.filter_by_category(category["toggle"], category["href"])
    expect(products_page.listing_heading(category["heading"])).to_be_visible()
    expect(products_page.product_cards.first).to_be_visible()


@pytest.mark.products
@pytest.mark.regression
@pytest.mark.p1
def test_products_brand_filter(page):
    """Matrix #23: the Polo brand link opens the filtered "Polo Products" list."""
    brand = products_td.BRAND_POLO
    products_page = ProductsPage(page)
    products_page.goto()
    products_page.filter_by_brand(brand["name"])
    expect(products_page.listing_heading(brand["heading"])).to_be_visible()
    expect(products_page.product_cards.first).to_be_visible()


@pytest.mark.products
@pytest.mark.regression
@pytest.mark.p1
def test_products_add_to_cart_shows_confirmation(page):
    """Matrix #24: adding from the grid shows the "Added!" confirmation modal."""
    products_page = ProductsPage(page)
    products_page.goto()
    products_page.add_to_cart(1)
    expect(products_page.added_to_cart_modal.root).to_be_visible()
    expect(products_page.added_to_cart_modal.view_cart_link).to_be_visible()


@pytest.mark.products
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.xfail(
    reason="Site defect: pressing Enter in the product search box does not submit the search — "
    "only clicking the Search button works.",
    strict=True,
)
def test_products_search_and_filters_keyboard_accessible(page):
    """Matrix #26: the search box is keyboard-reachable and Enter submits it."""
    products_page = ProductsPage(page)
    products_page.goto()
    products_page.search_input.focus()
    assert products_page.search_input_is_focused()
    page.keyboard.type(products_td.MATCHING_SEARCH_TERM)
    page.keyboard.press("Enter")
    expect(products_page.searched_products_heading).to_be_visible(timeout=5000)
