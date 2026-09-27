# Baseline of critical/serious axe violations each page already has —
# known site defects (see README "Defects found"). A test fails if a page
# gains a violation outside its baseline, or no longer has one in it (then
# the site fixed it: remove it here, the same way an XPASS is handled).
_SITE_WIDE = {
    "button-name",  # footer newsletter #subscribe button has no accessible name
    "color-contrast",  # low-contrast grey text on several elements
}

KNOWN_VIOLATIONS = {
    "/": _SITE_WIDE | {"link-name"},  # carousel prev/next arrows have no text
    "/login": _SITE_WIDE,
    "/products": _SITE_WIDE,
    "/view_cart": _SITE_WIDE,
    "/contact_us": _SITE_WIDE | {"label"},  # file upload input has no label
    "/product_details/1": _SITE_WIDE | {"label"},  # #quantity input has no label
}
