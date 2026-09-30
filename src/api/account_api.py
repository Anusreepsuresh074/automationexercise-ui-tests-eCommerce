import logging

import allure
from playwright.sync_api import APIRequestContext

logger = logging.getLogger(__name__)


class AccountApi:
    """The site's public account API (documented at /api_list), used for
    test setup and cleanup — faster and more reliable than driving the UI
    for steps that aren't what the test is verifying.

    The API always answers HTTP 200; the real outcome is the JSON body's
    responseCode."""

    def __init__(self, request: APIRequestContext):
        self.request = request

    def create_account(self, *, name: str, email: str, password: str, details: dict) -> None:
        # Context-manager steps (here and in delete_account) record no parameters,
        # so the password stays out of the Allure report.
        with allure.step(f"API: create account {email}"):
            form = {
                "name": name,
                "email": email,
                "password": password,
                "title": details["title"],
                "birth_date": details["day"],
                "birth_month": details["month"],
                "birth_year": details["year"],
                "firstname": details["first_name"],
                "lastname": details["last_name"],
                "address1": details["address1"],
                "country": details["country"],
                "state": details["state"],
                "city": details["city"],
                "zipcode": details["zipcode"],
                "mobile_number": details["mobile_number"],
            }
            body = self.request.post("/api/createAccount", form=form).json()
            if body.get("responseCode") != 201:
                raise RuntimeError(f"createAccount failed for {email}: {body}")
            logger.info("Created account %s via API", email)

    def delete_account(self, email: str, password: str) -> bool:
        """Deletes the account. Returns False (not an error) when it no
        longer exists — e.g. the test already deleted it through the UI."""
        with allure.step(f"API: delete account {email}"):
            body = self.request.delete("/api/deleteAccount", form={"email": email, "password": password}).json()
            code = body.get("responseCode")
            if code == 404:
                logger.info("Account %s already gone", email)
                return False
            if code != 200:
                raise RuntimeError(f"deleteAccount failed for {email}: {body}")
            logger.info("Deleted account %s via API", email)
            return True
