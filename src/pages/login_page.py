import allure
from playwright.sync_api import Page

from src.pages.base_page import BasePage


class LoginPage(BasePage):
    URL = "/login"

    def __init__(self, page: Page):
        super().__init__(page)
        self.login_email = page.get_by_test_id("login-email")
        self.login_password = page.get_by_test_id("login-password")
        self.login_button = page.get_by_test_id("login-button")
        self.login_error = page.get_by_text("Your email or password is incorrect!")
        self.signup_name = page.get_by_test_id("signup-name")
        self.signup_email = page.get_by_test_id("signup-email")
        self.signup_button = page.get_by_test_id("signup-button")
        self.signup_email_exists_error = page.get_by_text("Email Address already exist!")

    @allure.step("Log in as {email}")
    def login(self, email: str, password: str) -> None:
        self.login_email.fill(email)
        self.login_password.fill(password)
        self.login_button.click()

    @allure.step("Log out")
    def logout(self) -> None:
        self.nav_logout.click()
        self.page.wait_for_url(f"**{self.URL}")

    @allure.step("Start signup as {name} <{email}>")
    def start_signup(self, name: str, email: str) -> None:
        self.signup_name.fill(name)
        self.signup_email.fill(email)
        self.signup_button.click()
