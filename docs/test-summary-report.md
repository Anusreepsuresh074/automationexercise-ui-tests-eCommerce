# Test Summary Report: automationexercise.com UI Automation

| Version | Date | Author | Status |
|---|---|---|---|
| 1.0 | 2026-09-30 | Anusree P | Final for the current suite (58 tests from 48 designed cases) |

## 1. Summary

**The core shopping journeys work on all three browsers, but the site has 5 functional/accessibility defects and 5 axe-core accessibility violations, one of them present on every page.** The latest nightly full regression (GitHub Actions run [36534429526](https://github.com/Anusreepsuresh074/automationexercise-ui-tests-eCommerce/actions/runs/36534429526), 2026-09-29) finished with **53 passed and 5 xfailed (known defects) on each of Chromium, Firefox and WebKit, with no failures.** The highest-severity defect is that payment accepts a non-numeric card number and places the order (D-01).

## 2. Scope

| In scope | Out of scope |
|---|---|
| Browse, search and filter products; product details, quantity and reviews; cart (add, remove); signup; login and logout; checkout (address, payment, confirmation); account deletion; Contact Us; global navigation; axe-core scans of 6 key pages. Negative, boundary, auth-session and accessibility cases for each flow. | The static `Test Cases`, `API Testing` and `Video Tutorials` pages (only checked by the nav smoke test); mobile and tablet viewports; performance and load; the site's API beyond what test setup and cleanup use. |

The test design and traceability are in [`context/ui-test-case-matrix.md`](../context/ui-test-case-matrix.md). The site has no requirements document, so the expected behaviour comes from the live site and from rules recorded in [`context/ui-context.md`](../context/ui-context.md).

| Flow | Tests | Flow | Tests |
|---|---|---|---|
| login | 12 | contact_us | 4 |
| products | 8 | cart | 4 |
| product_details | 7 | checkout | 3 |
| nav | 7 | account | 2 |
| accessibility | 6 | signup | 5 |

## 3. Environment

| Item | Detail |
|---|---|
| Application | https://automationexercise.com (public production site, shared with other users) |
| Browsers | Chromium, Firefox, WebKit (Playwright 1.63.0 builds), desktop viewport 1920x1080 |
| Stack | Python 3.12, pytest 9.1.1, Playwright (sync API), pytest-xdist (`-n 4`), pytest-rerunfailures (2 retries), allure-pytest 2.16.1, axe-playwright-python 0.1.8 |
| Timeouts | Navigation 15 s, action 10 s, `expect` 10 s |
| Test data | One fixed, pre-registered account (from `.env` / CI secrets); throwaway accounts created and deleted through the site's API |
| CI | GitHub Actions on `ubuntu-latest` |

## 4. What runs where

| Trigger | Suite | Browsers | Allure report |
|---|---|---|---|
| Push / pull request to `main` | lint (ruff, mypy), then `-m smoke` (16 tests) | Chromium | Kept as a run artifact only |
| Nightly (01:30 UTC) and on demand | lint, then `-m regression` (all 58 tests) | Chromium, Firefox, WebKit in parallel jobs | Merged and published to the [live report](https://anusreepsuresh074.github.io/automationexercise-ui-tests-eCommerce/) with history |
| Locally | Any marker (`smoke`, `sanity`, `regression`, a flow, `accessibility`) | Any one browser per run | `reports/allure-results` |

## 5. Results

Nightly CI run of 2026-09-29 (whole workflow, including lint and the report, took about 3 minutes):

| Browser | Tests | Passed | Xfailed (known defect) | Failed | Retried | Test time |
|---|---|---|---|---|---|---|
| Chromium | 58 | 53 | 5 | 0 | 0 | 59 s |
| Firefox | 58 | 53 | 5 | 0 | 1 | 85 s |
| WebKit | 58 | 53 | 5 | 0 | 1 | 75 s |

The one retry on Firefox and WebKit was `test_checkout_happy_path` both times (on Firefox the cart did not yet show the added product; on WebKit "Proceed To Checkout" was not clickable within 10 s). It passed on the retry.

Local re-run on 2026-09-30 (Chromium, `-m regression -n 4`): **53 passed, 5 xfailed in 66 s**; smoke (`-m smoke`): **16 passed in 18 s**.

The previous nightly (2026-09-28) failed on Chromium only: 50 failed and 6 errors after retries, mostly `Locator.fill` timeouts, an account API call that returned a non-JSON response, and axe scans that no longer found the site's known violations. This points to the live site not serving its normal pages to that job. Firefox and WebKit in the same run passed (53 passed, 5 xfailed).

## 6. Defects

Each defect is pinned by a test marked `xfail(strict=True)`: the suite stays green, and if the site fixes the behaviour the test XPASSes and fails the run, so the marker is removed on purpose.

| ID | Defect | Severity | Test |
|---|---|---|---|
| D-01 | Payment accepts a non-numeric card number and places the order | High | `test_checkout_invalid_payment_details_rejected` |
| D-02 | Quantity field declares `min="1"`, but 0 is accepted and added to the cart | Medium | `test_product_details_quantity_below_minimum_rejected` |
| D-03 | Required mobile number accepts `123` and the account is created | Medium | `test_signup_invalid_mobile_number_format` |
| D-04 | Pressing Enter in product search does not submit it | Low (accessibility) | `test_products_search_and_filters_keyboard_accessible` |
| D-05 | Login email input has no `<label>` or `aria-label`, only a placeholder | Low (accessibility) | `test_login_fields_have_accessible_labels` |

**D-01: non-numeric card number accepted**
- Steps: log in; open `/product_details/1` (Blue Top) and add it to the cart; open the cart and click Proceed To Checkout; click Place Order; on `/payment` enter a valid name, CVC and expiry, card number `abcd1234`; click the Pay button.
- Expected: the card number is rejected and the user stays on `/payment`.
- Actual: the order is placed and the confirmation page is shown.

**D-02: quantity 0 accepted**
- Steps: open `/product_details/1`; set Quantity to `0`; click Add to cart; open the cart.
- Expected: nothing is added (the field declares `min="1"`).
- Actual: Blue Top is in the cart with quantity 0.

**D-03: 3-digit mobile number accepted**
- Steps: on `/login`, start signup with a new name and email; fill every required account detail with valid values, but Mobile Number `123`; click Create Account.
- Expected: the mobile number is rejected and no account is created.
- Actual: "Account Created!" is shown.

**D-04: Enter does not submit product search**
- Steps: open `/products`; focus the search box; type `Top`; press Enter.
- Expected: the "Searched Products" results are shown, as when clicking the Search button.
- Actual: nothing happens.

**D-05: login email has no accessible label**
- Steps: open `/login`; inspect the login form's email input.
- Expected: a `<label for>` or `aria-label` names the field.
- Actual: only a placeholder. A placeholder is not a label: it disappears once the user types, and not all assistive technology exposes it as the field's name.

Also recorded for a product decision, not as a defect: `/delete_account` has no server-side auth guard and shows "Account Deleted!" even when logged out (`test_unauthenticated_access_to_delete_account_not_guarded`).

## 7. Accessibility baseline

axe-core scans 6 pages (`/`, `/login`, `/products`, `/view_cart`, `/contact_us`, `/product_details/1`) and compares critical and serious violations against a baseline in [`tests/accessibility/accessibility_td.py`](../tests/accessibility/accessibility_td.py). A test fails if a page gains a new violation or loses a known one, so the baseline cannot go stale.

| axe rule | Where | Impact |
|---|---|---|
| `button-name`: newsletter subscribe button has no accessible name | All 6 pages (footer) | Critical |
| `color-contrast`: insufficient text contrast | All 6 pages | Serious |
| `link-name`: carousel previous/next arrows have no text | Home | Serious |
| `label`: file upload input has no label | Contact Us | Critical |
| `label`: quantity input has no label | Product details | Critical |

Automated scans find only part of the WCAG issues; no manual screen-reader audit was done.

## 8. Risks and limitations

- **Live, shared production site.** Slow page loads, outages and content changes by the site owner can fail tests that have nothing wrong with them (see the 28 Sep run). Retries absorb most of it, and they can also hide a real intermittent problem, so a `RERUN` in the report is worth a look.
- **`test_checkout_happy_path` is retry-prone** on Firefox and WebKit (section 5). It has not failed a run, but it should be investigated before it does.
- **One shared test account.** All authenticated tests, across parallel workers and any CI runs that overlap, log in as the same account, so a test that changes that account's state (for example its cart during checkout) could in principle affect another running at the same time.
- **Third-party ads are blocked** in every test. That removes a real source of flakiness (full-screen ad overlays), so the suite does not cover what real users see with ads on.
- **Desktop viewport only**; no mobile or tablet layouts.
- **Credentials in reports.** Steps that take the password record no parameters, its `repr()` is masked and failed tests' Playwright traces are rewritten with it masked. Reports published before this fix may still contain it, so the test account's password should be changed and the `TEST_PASSWORD` secret updated.
