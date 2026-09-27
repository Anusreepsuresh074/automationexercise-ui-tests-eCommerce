import pytest
from playwright.sync_api import expect

from src.core.browser_base import apply_storage_state_cookies
from src.pages.account_deleted_page import AccountDeletedPage
from src.pages.login_page import LoginPage
from tests.signup import signup_td


@pytest.mark.account
@pytest.mark.smoke
@pytest.mark.sanity
@pytest.mark.regression
@pytest.mark.p0
def test_delete_account_link_visibility(page, auth_storage_state):
    """Matrix #41: the Delete Account nav link is hidden while logged out
    and shown once logged in. Chosen as this flow's smoke test so smoke
    runs never delete an account."""
    login_page = LoginPage(page)
    login_page.goto()
    expect(login_page.nav_delete_account).to_have_count(0)

    apply_storage_state_cookies(page.context, auth_storage_state)
    login_page.goto()
    expect(login_page.nav_delete_account).to_be_visible()


@pytest.mark.account
@pytest.mark.regression
@pytest.mark.p1
def test_delete_account_completes(page, account_api, new_account):
    """Matrix #42: a user can delete their own account — immediately, with
    no confirmation step. The throwaway account is created through the
    API (setup, not what's under test); the login and deletion are driven
    through the UI. Never uses the shared test account."""
    account_api.create_account(**new_account, details=signup_td.ACCOUNT_DETAILS)

    login_page = LoginPage(page)
    login_page.goto()
    login_page.login(new_account["email"], new_account["password"])
    expect(login_page.logged_in_as(new_account["name"])).to_be_visible()

    deleted_page = AccountDeletedPage(page)
    deleted_page.delete_account()
    expect(deleted_page.heading).to_be_visible()
    expect(deleted_page.confirmation_text).to_be_visible()
    expect(deleted_page.nav_signup_login).to_be_visible()
    assert not account_api.delete_account(
        new_account["email"], new_account["password"]
    ), "account still exists after deleting it through the UI"
