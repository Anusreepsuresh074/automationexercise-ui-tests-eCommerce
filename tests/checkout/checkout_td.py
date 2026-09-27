ORDER_COMMENT = "Automated test order — please ignore."

VALID_CARD = {
    "name_on_card": "QA Portfolio Tester",
    "card_number": "4111111111111111",
    "cvc": "311",
    "expiry_month": "12",
    "expiry_year": "2030",
}
NON_NUMERIC_CARD = {**VALID_CARD, "card_number": "abcd1234"}
