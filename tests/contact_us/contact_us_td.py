from pathlib import Path

_DATA_DIR = Path(__file__).resolve().parents[1] / "data"

VALID_MESSAGE = {
    "name": "QA Contact Tester",
    "email": "qa.contact.54b9aef4@example.com",
    "subject": "Automation test inquiry",
    "message": "This is a test message submitted by an automated UI test.",
}
EMPTY_MESSAGE = {"name": "", "email": "", "subject": "", "message": ""}
MALFORMED_EMAIL = "not-an-email"

SMALL_ATTACHMENT = _DATA_DIR / "contact-us-attachment-small.txt"
LARGE_ATTACHMENT = _DATA_DIR / "contact-us-attachment-large.txt"  # ~68 KB, no documented limit
