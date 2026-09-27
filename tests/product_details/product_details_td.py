from dataclasses import dataclass


@dataclass(frozen=True)
class Product:
    id: int
    name: str
    price: str


BLUE_TOP = Product(id=1, name="Blue Top", price="Rs. 500")

LARGE_QUANTITY = "100"
BELOW_MINIMUM_QUANTITY = "0"  # the field declares min="1"
NON_NUMERIC_QUANTITY = "abc"

VALID_REVIEW = {
    "name": "QA Reviewer",
    "email": "qa.review.2e8a4654@example.com",
    "review": "Great quality product, fits as described.",
}
MALFORMED_EMAIL = "not-an-email"
