import pytest
from playwright.sync_api import expect

from src.pages.contact_us_page import ContactUsPage
from tests.contact_us import contact_us_td as td


@pytest.mark.contact_us
@pytest.mark.smoke
@pytest.mark.sanity
@pytest.mark.regression
@pytest.mark.p0
def test_contact_us_submit_valid(page):
    """Matrix #43: a complete message with an attachment is accepted after
    confirming the browser's "Press OK to proceed!" dialog."""
    contact_page = ContactUsPage(page)
    contact_page.goto()
    contact_page.fill_form(**td.VALID_MESSAGE)
    contact_page.attach_file(td.SMALL_ATTACHMENT)
    contact_page.submit()
    expect(contact_page.success_message).to_have_text("Success! Your details have been submitted successfully.")


@pytest.mark.contact_us
@pytest.mark.regression
@pytest.mark.p1
def test_contact_us_empty_required_fields(page):
    """Matrix #44: the required email field blocks an empty submission
    before the confirm dialog appears."""
    contact_page = ContactUsPage(page)
    contact_page.goto()
    contact_page.fill_form(**td.EMPTY_MESSAGE)
    contact_page.submit()
    assert contact_page.is_rejected_as_missing(contact_page.email)
    expect(contact_page.success_message).to_be_hidden()


@pytest.mark.contact_us
@pytest.mark.regression
@pytest.mark.p1
def test_contact_us_invalid_email_format(page):
    """Matrix #45: the email field's native validation rejects a malformed address."""
    contact_page = ContactUsPage(page)
    contact_page.goto()
    contact_page.fill_form(**{**td.VALID_MESSAGE, "email": td.MALFORMED_EMAIL})
    contact_page.submit()
    assert contact_page.is_rejected_as_malformed(contact_page.email)
    expect(contact_page.success_message).to_be_hidden()


@pytest.mark.contact_us
@pytest.mark.regression
@pytest.mark.p1
def test_contact_us_file_upload_boundary(page):
    """Matrix #46: a larger (~68 KB) attachment is accepted — no size
    limit is documented, and none is enforced at this size."""
    contact_page = ContactUsPage(page)
    contact_page.goto()
    contact_page.fill_form(**td.VALID_MESSAGE)
    contact_page.attach_file(td.LARGE_ATTACHMENT)
    contact_page.submit()
    expect(contact_page.success_message).to_be_visible()
