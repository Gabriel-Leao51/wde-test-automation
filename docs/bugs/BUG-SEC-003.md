# BUG-SEC-003: CSRF Token Exposed in the URL (Query String)

## Severity

**MEDIUM-LOW**

- **Justification:** The CSRF token itself is still correctly validated by the server (confirmed: requests without a token or with an invalid token are rejected — see `BUG-INFO-001` for the problem *in how it responds* to that rejection). The risk here is the **exposure channel**: putting the token in the URL means it gets written to server access logs, the browser's history, and can potentially leak to third parties via the `Referer` header when the page loads external resources.

## Priority

**MEDIUM**

## Environment

- **Application:** WDE Shop
- **Base URL:** `http://localhost:3000`
- **Affected Endpoint:** `/admin/products/new`, `/admin/products/:id` (product form) — the responsible code pattern (`views/admin/products/includes/product-form.ejs`) is shared by both screens.

## Report Details

- **Reported by:** Gabriel Leão (with assistance from Claude)
- **Date discovered:** 2026-07-24

## Steps to Reproduce

1. Log in as `admin`.
2. Go to `/admin/products/new`.
3. Inspect the product form's `action` attribute (or observe the URL after a failed submit).

## Expected Result

The CSRF token should only be sent as a hidden field (`<input type="hidden" name="_csrf">`) inside the form body — never as a URL parameter.

## Actual Result (Failure)

`views/admin/products/includes/product-form.ejs` builds the form's `action` like this:

```html
<form action="<%= submitPath %>?_csrf=<%= locals.csrfToken %>" method="POST" enctype="multipart/form-data">
```

The token appears directly in the form's target URL (e.g. `/admin/products?_csrf=AbCdEf123...`).

## Evidence

- **Automated Test:** `features/security/hardening.feature`, scenario "The CSRF token should not be exposed in the product form URL" (`@xfail`, tag `@csrf`).
- **Source code:** `wde/views/admin/products/includes/product-form.ejs`.

Note: every other form in the application (login, cart, logout, orders) correctly uses `<input type="hidden" name="_csrf" ...>` — this problematic pattern is isolated to the product form.

## Root Cause Analysis

The product form uses `enctype="multipart/form-data"` (required for image upload). It seems the token was put in the URL as a way to guarantee it would be sent regardless of the file's presence — but a hidden field inside a `<form multipart>` works normally and is the pattern already used by every other form with upload/submit in the application.

## Potential Impact

- The CSRF token ends up in server access logs (usually retained longer than the session itself).
- It's recorded in the admin's browser navigation history.
- It can leak via the `Referer` header to any third-party resource loaded from that page (fonts, scripts, external images).
- Reduces the effectiveness of CSRF protection if the token leaks through any of these channels while still valid within the session window.

## Recommendations

1. Change `product-form.ejs` to use `action="<%= submitPath %>"` (no query string) and add `<input type="hidden" name="_csrf" value="<%= locals.csrfToken %>">` inside the form, matching the pattern already used by every other form in the application.
