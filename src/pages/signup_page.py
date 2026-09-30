import allure
from playwright.sync_api import Page

from src.pages.base_page import BasePage


class SignupPage(BasePage):
    URL = "/signup"

    def __init__(self, page: Page):
        super().__init__(page)
        self.title_mr = page.locator("#id_gender1")
        self.title_mrs = page.locator("#id_gender2")
        self.password = page.get_by_test_id("password")
        self.birth_day = page.get_by_test_id("days")
        self.birth_month = page.get_by_test_id("months")
        self.birth_year = page.get_by_test_id("years")
        self.first_name = page.get_by_test_id("first_name")
        self.last_name = page.get_by_test_id("last_name")
        self.address1 = page.get_by_test_id("address")
        self.country = page.get_by_test_id("country")
        self.state = page.get_by_test_id("state")
        self.city = page.get_by_test_id("city")
        self.zipcode = page.get_by_test_id("zipcode")
        self.mobile_number = page.get_by_test_id("mobile_number")
        self.create_account_button = page.get_by_test_id("create-account")

    def fill_account_details(
        self,
        *,
        title: str,
        password: str,
        day: str,
        month: str,
        year: str,
        first_name: str,
        last_name: str,
        address1: str,
        country: str,
        state: str,
        city: str,
        zipcode: str,
        mobile_number: str,
    ) -> None:
        # Context-manager step so the password isn't recorded as a step parameter.
        with allure.step("Fill account details"):
            (self.title_mrs if title == "Mrs" else self.title_mr).check()
            self.password.fill(password)
            self.birth_day.select_option(day)
            self.birth_month.select_option(month)
            self.birth_year.select_option(year)
            self.first_name.fill(first_name)
            self.last_name.fill(last_name)
            self.address1.fill(address1)
            self.country.select_option(country)
            self.state.fill(state)
            self.city.fill(city)
            self.zipcode.fill(zipcode)
            self.mobile_number.fill(mobile_number)

    @allure.step("Submit account details")
    def submit(self) -> None:
        self.create_account_button.click()
