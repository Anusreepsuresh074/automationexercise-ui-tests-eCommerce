import logging
import os
import re

import allure
import pytest

from src.core.browser_base import launch_browser, new_context
from src.pages.login_page import LoginPage
from src.utils.resource_registry import record_created_resource
from tests.signup import signup_td

logger = logging.getLogger(__name__)

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
AUTH_DIR = os.path.join(ROOT_DIR, "auth")
TRACES_DIR = os.path.join(ROOT_DIR, "reports", "traces")


@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(item, call):
    """On a test failure, attaches a screenshot and the test's Playwright
    trace to its Allure result. Done here, not in fixture teardown, so the
    attachments land on the test itself rather than its teardown step."""
    report = yield
    context = getattr(item, "_pw_context", None)
    if report.when == "call" and report.failed and context is not None:
        _attach_failure_artifacts(item, context)
    return report


def _attach_failure_artifacts(item, context):
    open_pages = [p for p in context.pages if not p.is_closed()]
    if open_pages:
        screenshot = open_pages[-1].screenshot(full_page=True)
        allure.attach(screenshot, name="screenshot", attachment_type=allure.attachment_type.PNG)
    os.makedirs(TRACES_DIR, exist_ok=True)
    trace_path = os.path.join(TRACES_DIR, re.sub(r"[^\w.-]+", "_", item.nodeid) + ".zip")
    context.tracing.stop(path=trace_path)
    item._pw_trace_saved = True
    allure.attach.file(trace_path, name="playwright-trace (open with: playwright show-trace)", extension="zip")
    logger.info("Saved failure trace to %s", trace_path)


@pytest.fixture(autouse=True)
def _allure_labels(request, browser_name):
    """Groups results by flow (the test's folder) in the Allure report, maps
    the p0/p1 priority markers to Allure severity, and tags the browser.
    The browser is also a test parameter, so when CI merges all browsers'
    results into one report, each browser's run counts as its own result
    instead of being folded in as a retry of another browser's."""
    allure.dynamic.feature(request.node.path.parent.name)
    if request.node.get_closest_marker("p0"):
        allure.dynamic.severity(allure.severity_level.CRITICAL)
    elif request.node.get_closest_marker("p1"):
        allure.dynamic.severity(allure.severity_level.NORMAL)
    allure.dynamic.tag(browser_name)
    allure.dynamic.parameter("browser", browser_name)


@pytest.fixture(scope="session")
def browser(playwright_instance, browser_name, request):
    browser = launch_browser(playwright_instance, browser_name, headless=not request.config.getoption("--headed"))
    yield browser
    browser.close()


@pytest.fixture(scope="session")
def auth_storage_state(browser, config, test_user):
    """Logs in once per run (once per worker under pytest-xdist) through the
    real login form and caches the session — cookies incl. the httpOnly
    sessionid — for every authenticated test to start from. Tests of the
    login flow itself don't use this; they drive LoginPage directly."""
    worker = os.environ.get("PYTEST_XDIST_WORKER", "main")
    path = os.path.join(AUTH_DIR, f"state-{worker}.json")
    context = new_context(browser, config)
    try:
        page = context.new_page()
        login_page = LoginPage(page)
        login_page.goto()
        login_page.login(test_user.email, test_user.password)
        page.wait_for_url(config.base_url + "/")
        context.storage_state(path=path)
    finally:
        context.close()
    logger.info("Cached login session for %s at %s", test_user.email, path)
    return path


def _isolated_context(request, browser, config, storage_state=None):
    """A fresh browser context per test — no cookies, storage, routes or
    event listeners carry over from another test. Traced from the start;
    the trace is kept only if the test fails."""
    context = new_context(browser, config, storage_state=storage_state)
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    request.node._pw_context = context
    request.node._pw_trace_saved = False  # the same item is reused by --reruns
    yield context
    if not request.node._pw_trace_saved:
        context.tracing.stop()
    context.close()


@pytest.fixture
def context(request, browser, config):
    yield from _isolated_context(request, browser, config)


@pytest.fixture
def page(context):
    """A new page in a fresh, logged-out guest session."""
    return context.new_page()


@pytest.fixture
def authenticated_context(request, browser, config, auth_storage_state):
    yield from _isolated_context(request, browser, config, storage_state=auth_storage_state)


@pytest.fixture
def authenticated_page(authenticated_context):
    """A new page, already logged in as the fixed test account."""
    return authenticated_context.new_page()


@pytest.fixture
def new_account(account_api, config):
    """Credentials for a throwaway account, unique to this test. The test
    decides how the account gets created (UI signup, or account_api for
    setup); either way it is deleted through the API afterwards, so runs
    never leave orphaned accounts on the site — even if the test failed
    halfway."""
    account = {"name": signup_td.SIGNUP_NAME, "email": signup_td.fresh_email(), "password": signup_td.fresh_password()}
    record_created_resource("user_account", account["email"], config.env)
    yield account
    account_api.delete_account(account["email"], account["password"])
