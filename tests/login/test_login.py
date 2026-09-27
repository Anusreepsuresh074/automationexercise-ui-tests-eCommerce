import re

import pytest
from playwright.sync_api import expect

from src.pages.account_deleted_page import AccountDeletedPage
from src.pages.login_page import LoginPage
from tests.login import login_td


@pytest.mark.login
@pytest.mark.smoke
@pytest.mark.sanity
@pytest.mark.regression
@pytest.mark.p0
def test_login_valid_credentials(page, config, test_user):
    """Matrix #1: a registered user can log in and lands on the home page."""
    login_page = LoginPage(page)
    login_page.goto()
    login_page.login(test_user.email, test_user.password)
    expect(page).to_have_url(config.base_url + "/")
    expect(login_page.logged_in_as(test_user.name)).to_be_visible()
    expect(login_page.nav_logout).to_be_visible()


@pytest.mark.login
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.parametrize("email,password", login_td.INVALID_CREDENTIALS)
def test_login_invalid_credentials(page, test_user, email, password):
    """Matrix #2, #3: wrong password and unregistered email both show the
    same generic error and never log the user in."""
    login_page = LoginPage(page)
    login_page.goto()
    login_page.login(email or test_user.email, password)
    expect(login_page.login_error).to_be_visible()
    expect(page).to_have_url(re.compile(rf"{LoginPage.URL}$"))
    expect(login_page.nav_logout).to_have_count(0)


@pytest.mark.login
@pytest.mark.regression
@pytest.mark.p1
def test_login_malformed_email_format(page):
    """Matrix #4: the email field's native type="email" validation blocks
    the submission before it reaches the server."""
    login_page = LoginPage(page)
    login_page.goto()
    login_page.login(login_td.MALFORMED_EMAIL, "Whatever-123!")
    assert login_page.is_rejected_as_malformed(login_page.login_email)
    expect(page).to_have_url(re.compile(rf"{LoginPage.URL}$"))
    expect(login_page.nav_logout).to_have_count(0)


@pytest.mark.login
@pytest.mark.regression
@pytest.mark.p1
def test_login_empty_fields(page):
    """Matrix #5: both fields are required — the browser blocks an empty
    submission."""
    login_page = LoginPage(page)
    login_page.goto()
    login_page.login("", "")
    assert login_page.is_rejected_as_missing(login_page.login_email)
    expect(page).to_have_url(re.compile(rf"{LoginPage.URL}$"))
    expect(login_page.nav_logout).to_have_count(0)


@pytest.mark.login
@pytest.mark.regression
@pytest.mark.p1
def test_login_long_password_input(page, test_user):
    """Matrix #6: a 500-character password (the field has no maxlength) is
    handled like any wrong password — the normal error, no crash."""
    login_page = LoginPage(page)
    login_page.goto()
    login_page.login(test_user.email, login_td.LONG_PASSWORD)
    expect(login_page.login_error).to_be_visible()
    expect(login_page.nav_logout).to_have_count(0)


@pytest.mark.login
@pytest.mark.sanity
@pytest.mark.regression
@pytest.mark.p0
def test_logout_ends_session(page, test_user):
    """Matrix #7: logging out returns to /login and removes the logged-in
    nav. Logs in fresh rather than using the cached session, because
    logout invalidates the session server-side for every later test."""
    login_page = LoginPage(page)
    login_page.goto()
    login_page.login(test_user.email, test_user.password)
    expect(login_page.nav_logout).to_be_visible()
    login_page.logout()
    expect(page).to_have_url(re.compile(rf"{LoginPage.URL}$"))
    expect(login_page.login_button).to_be_visible()
    expect(login_page.nav_logout).to_have_count(0)


@pytest.mark.login
@pytest.mark.sanity
@pytest.mark.regression
@pytest.mark.p0
def test_unauthenticated_access_to_delete_account_not_guarded(page):
    """Matrix #8: /delete_account has no server-side auth guard — while
    logged out it still renders "Account Deleted!" (only the nav link is
    hidden). Low impact since there is no account to delete, but a real
    authorization gap, so this test pins the current behavior."""
    deleted_page = AccountDeletedPage(page)
    deleted_page.delete_account()
    expect(deleted_page.heading).to_be_visible()


@pytest.mark.login
@pytest.mark.sanity
@pytest.mark.regression
@pytest.mark.p0
def test_session_expired_mid_use(authenticated_page, test_user):
    """Matrix #9: once the session cookie is gone, the next page load shows
    the logged-out state instead of a broken page."""
    login_page = LoginPage(authenticated_page)
    authenticated_page.context.clear_cookies(name="sessionid")
    authenticated_page.goto("/")
    expect(login_page.nav_signup_login).to_be_visible()
    expect(login_page.logged_in_as(test_user.name)).to_have_count(0)


@pytest.mark.login
@pytest.mark.regression
@pytest.mark.p1
def test_login_keyboard_only_operable(page, test_user):
    """Matrix #10: the login form can be completed with the keyboard alone
    (Tab between fields, Enter to submit)."""
    login_page = LoginPage(page)
    login_page.goto()
    login_page.login_email.focus()
    page.keyboard.type(test_user.email)
    page.keyboard.press("Tab")
    page.keyboard.type(test_user.password)
    page.keyboard.press("Tab")
    page.keyboard.press("Enter")
    expect(login_page.logged_in_as(test_user.name)).to_be_visible()


@pytest.mark.login
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.xfail(
    reason="Site defect: the login email input has no <label> or aria-label, only a placeholder.",
    strict=True,
)
def test_login_fields_have_accessible_labels(page):
    """Matrix #11: the email input should have an accessible name beyond
    its placeholder."""
    login_page = LoginPage(page)
    login_page.goto()
    # Not to_have_accessible_name(): browsers fall back to the placeholder
    # for the accessible name, which would hide exactly this gap.
    input_id = login_page.login_email.get_attribute("id") or ""
    has_label = page.locator(f'label[for="{input_id}"]').count() > 0 if input_id else False
    has_aria_label = bool(login_page.login_email.get_attribute("aria-label"))
    assert has_label or has_aria_label, "email input has no accessible name beyond its placeholder"


@pytest.mark.login
@pytest.mark.regression
@pytest.mark.p1
def test_login_network_failure_does_not_create_session(page, test_user):
    """Matrix #12: if the login request fails at the network level, no
    session is created — the user is still logged out once connectivity
    returns. (The site shows no error of its own; the browser shows its
    offline page.)"""
    login_page = LoginPage(page)
    login_page.goto()
    page.route(f"**{LoginPage.URL}", lambda route: route.abort())
    login_page.login(test_user.email, test_user.password)
    page.unroute_all()
    page.goto("/")
    expect(login_page.nav_signup_login).to_be_visible()
    expect(login_page.logged_in_as(test_user.name)).to_have_count(0)
