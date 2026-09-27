import pytest

# Same outcome expected for both: the generic "incorrect" error, never a
# hint about which part was wrong. email=None means the registered test
# account's own email (resolved from the test_user fixture at run time).
INVALID_CREDENTIALS = [
    pytest.param(None, "wrong-Password-000", id="wrong-password"),
    pytest.param("qa.nonexistent.b3f0c1a2@example.com", "Whatever-123!", id="unregistered-email"),
]

MALFORMED_EMAIL = "not-an-email"
LONG_PASSWORD = "x" * 500
