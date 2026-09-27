import secrets
import string


def fresh_email() -> str:
    return f"qa.signup.{secrets.token_hex(4)}@example.com"


def fresh_password() -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(14)) + "!9"


SIGNUP_NAME = "QA Signup Tester"
MALFORMED_EMAIL = "no-at-sign.com"
INVALID_MOBILE_NUMBER = "123"

ACCOUNT_DETAILS = {
    "title": "Mrs",
    "day": "15",
    "month": "June",
    "year": "1995",
    "first_name": "QA",
    "last_name": "Signup",
    "address1": "123 Test Street",
    "country": "India",
    "state": "Kerala",
    "city": "Kochi",
    "zipcode": "682001",
    "mobile_number": "+916539100431",
}
