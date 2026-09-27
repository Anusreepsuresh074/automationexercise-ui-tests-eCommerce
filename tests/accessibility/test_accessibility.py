import pytest

from src.utils.accessibility import blocking_violations, scan_accessibility
from tests.accessibility.accessibility_td import KNOWN_VIOLATIONS


@pytest.mark.accessibility
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.parametrize("path", KNOWN_VIOLATIONS)
def test_no_new_accessibility_violations(page, path):
    """Matrix #48: an automated axe-core (WCAG) scan of each key page finds
    no critical/serious violations beyond the page's known baseline — so
    new accessibility regressions fail the build while existing defects
    stay tracked."""
    page.goto(path)
    found = blocking_violations(scan_accessibility(page))
    known = KNOWN_VIOLATIONS[path]
    new, fixed = found - known, known - found
    assert not new, f"new accessibility violations on {path}: {sorted(new)} (details in the Allure attachment)"
    assert not fixed, f"{path} no longer violates {sorted(fixed)} — remove from KNOWN_VIOLATIONS"
