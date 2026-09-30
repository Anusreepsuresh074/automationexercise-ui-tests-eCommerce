import json
import os
import platform
from importlib.metadata import version

import pytest
from dotenv import load_dotenv
from playwright.sync_api import expect, sync_playwright

from src.api.account_api import AccountApi
from src.config.config_loader import Secret, load_config, load_test_user

load_dotenv()


def pytest_assertrepr_compare(op, left, right):
    """pytest diffs two strings by their raw text, bypassing repr(); keep a
    Secret (the test account's password) out of assertion diffs."""
    if isinstance(left, Secret) or isinstance(right, Secret):
        return [f"{left!r} {op} {right!r}", "(diff hidden: the comparison involves a secret)"]
    return None


def pytest_addoption(parser):
    parser.addoption(
        "--env",
        action="store",
        default=None,
        help="Environment to test against, as defined in config/config.yaml (default: $TEST_ENV or prod)",
    )
    parser.addoption(
        "--browser",
        action="store",
        default="chromium",
        choices=["chromium", "firefox", "webkit"],
        help="Browser to run the suite in for this invocation",
    )
    parser.addoption(
        "--headed",
        action="store_true",
        default=os.getenv("HEADED") == "1",
        help="Run in a visible browser window (also: HEADED=1)",
    )


# Buckets failures in the Allure report's "Categories" tab, so a reader
# can tell known site defects and live-site slowness from real regressions.
_ALLURE_CATEGORIES = [
    {"name": "Known site defects (xfail)", "matchedStatuses": ["skipped"], "messageRegex": ".*Site defect.*"},
    {"name": "Live site too slow (timeouts)", "matchedStatuses": ["broken", "failed"], "messageRegex": ".*Timeout.*"},
    {"name": "Assertion failures — possible regressions", "matchedStatuses": ["failed"]},
    {"name": "Test/framework errors", "matchedStatuses": ["broken"]},
]


def pytest_sessionstart(session):
    """Writes the Allure report's Environment panel and failure categories.
    Only on the controller process — not repeated by every xdist worker."""
    alluredir = session.config.getoption("allure_report_dir", None)
    if not alluredir or os.environ.get("PYTEST_XDIST_WORKER"):
        return
    os.makedirs(alluredir, exist_ok=True)
    config = load_config(env=session.config.getoption("--env"))
    environment = {
        "Environment": config.env,
        "Base_URL": config.base_url,  # no spaces: .properties treats a space as the separator
        "Browser": session.config.getoption("--browser"),
        "Viewport": f"{config.viewport.width}x{config.viewport.height}",
        "Python": platform.python_version(),
        "Playwright": version("playwright"),
    }
    with open(os.path.join(alluredir, "environment.properties"), "w") as f:
        f.writelines(f"{key}={value}\n" for key, value in environment.items())
    with open(os.path.join(alluredir, "categories.json"), "w") as f:
        json.dump(_ALLURE_CATEGORIES, f, indent=2)


@pytest.fixture(scope="session")
def config(request):
    config = load_config(env=request.config.getoption("--env"))
    expect.set_options(timeout=config.timeouts.expect_ms)
    return config


@pytest.fixture(scope="session")
def test_user():
    return load_test_user()


@pytest.fixture(scope="session")
def browser_name(request):
    return request.config.getoption("--browser")


@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as p:
        # The site tags its interactive elements with data-qa="..." —
        # lets page objects use get_by_test_id() for them.
        p.selectors.set_test_id_attribute("data-qa")
        yield p


@pytest.fixture(scope="session")
def api_request(playwright_instance, config):
    request = playwright_instance.request.new_context(base_url=config.base_url)
    yield request
    request.dispose()


@pytest.fixture(scope="session")
def account_api(api_request):
    return AccountApi(api_request)
