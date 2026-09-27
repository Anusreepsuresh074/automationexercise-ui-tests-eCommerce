import pytest
from playwright.sync_api import expect

from src.pages.base_page import BasePage
from tests.nav.nav_td import IN_SCOPE_NAV_LINKS


@pytest.mark.nav
@pytest.mark.smoke
@pytest.mark.sanity
@pytest.mark.regression
@pytest.mark.p0
@pytest.mark.parametrize("path", IN_SCOPE_NAV_LINKS)
def test_global_nav_link_resolves(page, path):
    """Matrix #47: every in-scope nav destination loads with a 2xx
    response and a rendered header. The only coverage the static Test
    Cases / API Testing pages get."""
    response = page.goto(path)
    assert response is not None and response.ok, f"{path} returned {response and response.status}"
    expect(BasePage(page).header).to_be_visible()
