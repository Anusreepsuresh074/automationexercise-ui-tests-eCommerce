import re

import pytest
from playwright.sync_api import expect

from src.pages.account_created_page import AccountCreatedPage
from src.pages.login_page import LoginPage
from src.pages.signup_page import SignupPage
from tests.signup import signup_td


def _open_signup_form(page, account) -> SignupPage:
    login_page = LoginPage(page)
    login_page.goto()
    login_page.start_signup(account["name"], account["email"])
    return SignupPage(page)


@pytest.mark.signup
@pytest.mark.smoke
@pytest.mark.sanity
@pytest.mark.regression
@pytest.mark.p0
def test_signup_happy_path(page, new_account):
    """Matrix #13: a new user can sign up, lands on "Account Created!",
    and is logged in on continuing."""
    signup_page = _open_signup_form(page, new_account)
    signup_page.fill_account_details(password=new_account["password"], **signup_td.ACCOUNT_DETAILS)
    signup_page.submit()

    created_page = AccountCreatedPage(page)
    expect(created_page.heading).to_be_visible()
    created_page.continue_to_home()
    expect(created_page.logged_in_as(new_account["name"])).to_be_visible()


@pytest.mark.signup
@pytest.mark.regression
@pytest.mark.p1
def test_signup_duplicate_email(page, test_user):
    """Matrix #14: signing up with an already-registered email shows
    "Email Address already exist!" and never shows the account form."""
    login_page = LoginPage(page)
    login_page.goto()
    login_page.start_signup("Dup Test", test_user.email)
    expect(login_page.signup_email_exists_error).to_be_visible()
    expect(SignupPage(page).password).to_have_count(0)


@pytest.mark.signup
@pytest.mark.regression
@pytest.mark.p1
def test_signup_missing_required_field(page, new_account):
    """Matrix #15: the mobile number is required — the browser blocks the
    submission and no account is created."""
    signup_page = _open_signup_form(page, new_account)
    signup_page.fill_account_details(
        password=new_account["password"], **{**signup_td.ACCOUNT_DETAILS, "mobile_number": ""}
    )
    signup_page.submit()
    assert signup_page.is_rejected_as_missing(signup_page.mobile_number)
    expect(page).to_have_url(re.compile(rf"{SignupPage.URL}$"))


@pytest.mark.signup
@pytest.mark.regression
@pytest.mark.p1
def test_signup_malformed_email_format(page):
    """Matrix #16: the signup email field's native validation blocks a
    malformed address before reaching /signup."""
    login_page = LoginPage(page)
    login_page.goto()
    login_page.start_signup("QA Test", signup_td.MALFORMED_EMAIL)
    assert login_page.is_rejected_as_malformed(login_page.signup_email)
    expect(page).to_have_url(re.compile(rf"{LoginPage.URL}$"))


@pytest.mark.signup
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.xfail(
    reason="Site defect: the required mobile number field accepts '123' and the account is created.",
    strict=True,
)
def test_signup_invalid_mobile_number_format(page, new_account):
    """Matrix #17: a 3-digit mobile number should be rejected."""
    signup_page = _open_signup_form(page, new_account)
    signup_page.fill_account_details(
        password=new_account["password"],
        **{**signup_td.ACCOUNT_DETAILS, "mobile_number": signup_td.INVALID_MOBILE_NUMBER},
    )
    signup_page.submit()
    page.wait_for_load_state("load")  # let an accepted signup finish navigating
    expect(AccountCreatedPage(page).heading, "account was created with mobile number '123'").to_have_count(0)
