from pathlib import Path

import allure
from playwright.sync_api import Page

from src.pages.base_page import BasePage


class ContactUsPage(BasePage):
    URL = "/contact_us"

    def __init__(self, page: Page):
        super().__init__(page)
        self.name = page.get_by_test_id("name")
        self.email = page.get_by_test_id("email")
        self.subject = page.get_by_test_id("subject")
        self.message = page.get_by_test_id("message")
        self.attachment = page.locator('input[name="upload_file"]')
        self.submit_button = page.get_by_test_id("submit-button")
        # Scoped to the form panel: the same text also matches a second
        # element elsewhere on the page after a real submission.
        self.success_message = page.locator("#contact-page .status.alert-success")

    @allure.step("Fill contact form")
    def fill_form(self, *, name: str, email: str, subject: str, message: str) -> None:
        self.name.fill(name)
        self.email.fill(email)
        self.subject.fill(subject)
        self.message.fill(message)

    @allure.step("Attach file")
    def attach_file(self, file_path: str | Path) -> None:
        self.attachment.set_input_files(file_path)

    @allure.step("Submit contact form")
    def submit(self) -> None:
        # Submitting opens a native confirm() ("Press OK to proceed!") that
        # must be accepted. Only fires if the browser's own validation passes.
        self.page.once("dialog", lambda dialog: dialog.accept())
        self.submit_button.click()
