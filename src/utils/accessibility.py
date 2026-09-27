import json

import allure
from axe_playwright_python.sync_playwright import Axe
from playwright.sync_api import Page

_axe = Axe()

# Impacts that count as a regression. "moderate"/"minor" findings (landmark
# and heading structure) are still in the attached report, but don't fail.
BLOCKING_IMPACTS = {"critical", "serious"}


@allure.step("Run axe accessibility scan")
def scan_accessibility(page: Page) -> dict[str, str]:
    """Runs axe-core (WCAG rules) on the current page, attaches the full
    result to the Allure report, and returns {rule_id: impact} for every
    rule the page violates."""
    result = _axe.run(page)
    violations = result.response["violations"]
    allure.attach(
        json.dumps(violations, indent=2),
        name="axe violations",
        attachment_type=allure.attachment_type.JSON,
    )
    return {v["id"]: v["impact"] for v in violations}


def blocking_violations(violations: dict[str, str]) -> set[str]:
    return {rule for rule, impact in violations.items() if impact in BLOCKING_IMPACTS}
