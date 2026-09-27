import json
import re

from playwright.sync_api import Browser, BrowserContext, BrowserType, Playwright

from src.config.config_loader import Config

_LAUNCHERS: dict[str, str] = {
    "chromium": "chromium",
    "firefox": "firefox",
    "webkit": "webkit",
}


def launch_browser(playwright: Playwright, browser_name: str, headless: bool = True) -> Browser:
    if browser_name not in _LAUNCHERS:
        raise ValueError(f"Unsupported browser '{browser_name}'. Supported: {list(_LAUNCHERS)}")

    browser_type: BrowserType = getattr(playwright, _LAUNCHERS[browser_name])
    return browser_type.launch(headless=headless)


# Third-party ad networks the site embeds. Google's full-screen "vignette"
# interstitial (URL gains #google_vignette) randomly overlays the page and
# swallows clicks — confirmed as the cause of intermittent category-filter
# failures. Ads are outside the app under test, so block them outright.
_BLOCKED_AD_HOSTS = re.compile(
    r"^https?://([^/]+\.)?(googlesyndication\.com|doubleclick\.net|googleadservices\.com"
    r"|adservice\.google\.[a-z.]+|fundingchoicesmessages\.google\.com|googletagservices\.com)/"
)


def new_context(browser: Browser, config: Config, storage_state: str | None = None) -> BrowserContext:
    context = browser.new_context(
        base_url=config.base_url,
        viewport={"width": config.viewport.width, "height": config.viewport.height},
        storage_state=storage_state,
    )
    context.set_default_navigation_timeout(config.timeouts.navigation_ms)
    context.set_default_timeout(config.timeouts.action_ms)
    context.route(_BLOCKED_AD_HOSTS, lambda route: route.abort())
    return context


def apply_storage_state_cookies(context: BrowserContext, storage_state_path: str) -> None:
    with open(storage_state_path) as f:
        context.add_cookies(json.load(f)["cookies"])
