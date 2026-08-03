# Roadmap: Cypress + Cucumber (JS) → Playwright + pytest-bdd (Python) Migration

## 1. Context

This project (`wde_automacao`) contains an E2E suite in **Cypress + `@badeball/cypress-cucumber-preprocessor`**, testing the **WDE Shop** application (`https://wde-5p3f.onrender.com`). Current coverage:

- **Admin:** login (happy/negative path), authentication (401), authorization (403 / known bugs), product CRUD, order management.
- **Customer:** E2E purchase flow (login → product → cart → Stripe redirect).
- **Documented security findings:** `BUG-AUTH-001` (authorization bypass on `/admin/products`) and `BUG-AUTH-002` (order data leak on `/admin/orders`), with evidence in `evidence/`.

Decisions already made for the migration:

| Decision | Choice |
|---|---|
| Language | **Python** |
| BDD | Keep Gherkin (`.feature`), via **pytest-bdd** |
| Runner/Browser | **pytest-playwright** (official Playwright for Python) |
| Package manager | **uv** |
| Execution mode | Roadmap first → implementation phase by phase |

This is a project that's **new on the inside** (a language change, not just a framework change), but keeps: the same `.feature` files (now in English — see Phase 10), the same Page Object Model, the same test data, and the same bug reports/evidence — only the execution layer changes.

## 2. Why this stack

- **pytest-bdd**: maps `.feature` files to pytest tests via `@scenario`/`scenarios()`; gains the whole pytest ecosystem (fixtures, `-n auto` with `pytest-xdist`, `pytest-html`, `@happy-path`/`@negative-path` markers as pytest marks).
- **pytest-playwright**: official plugin (`page`, `browser`, `context` fixtures ready to use; `--browser`, `--headed`, `--tracing`, `--video` via CLI).
- **Real simplification vs. Cypress**: the Stripe checkout test used `cy.origin()` to work around Cypress's cross-origin limitation and still couldn't interact with Stripe's iframe. Playwright **doesn't have this limitation** — cross-origin navigation and iframes are native. This opened up the possibility of, in the future, completing the test payment flow (see Phase 9).

## 3. Proposed directory structure

```
wde_automacao/
├── pyproject.toml              # uv + pytest + pytest-bdd + pytest-playwright
├── uv.lock
├── pytest.ini                  # or [tool.pytest.ini_options] in pyproject
├── conftest.py                 # base_url, login/role fixtures, feature paths
├── features/
│   ├── admin/
│   │   ├── authentication.feature
│   │   ├── authorization.feature
│   │   ├── login.feature
│   │   └── manage_orders.feature
│   │   └── manage_product.feature
│   └── client/
│       └── purchase_flow.feature
├── steps/
│   ├── __init__.py
│   ├── test_admin_login_steps.py
│   ├── test_common_steps.py
│   ├── test_manage_orders_steps.py
│   ├── test_manage_product_steps.py
│   ├── test_purchase_flow_steps.py
│   └── test_security_steps.py
├── pages/
│   ├── __init__.py
│   ├── login_page.py
│   ├── products_page.py
│   ├── cart_page.py
│   └── orders_page.py
├── test_data/                  # equivalent to cypress/fixtures
│   ├── users.json
│   ├── orders.json
│   └── mousepad.jpg
├── utils/
│   └── helpers.py              # format_product_data()
├── docs/bugs/                  # kept as-is
├── evidence/                   # kept as-is
├── .github/workflows/
│   └── playwright-tests.yml
└── README.md                   # rewritten for the Python stack
```

`features/` is kept separate from `steps/` (unlike Cypress, which unified everything under `support/`) because that's the idiomatic pytest-bdd pattern and avoids ambiguity between "step definition" and "test file" in pytest.

## 4. Cypress → Playwright/pytest-bdd Mapping

| Cypress | Playwright/Python | Notes |
|---|---|---|
| `cy.visit(path)` | `page.goto(path)` | `base_url` via `pytest-playwright` (`--base-url` or fixture) |
| `cy.get(selector)` | `page.locator(selector)` | prefer `get_by_role`/`get_by_label`/`get_by_text` where it makes sense |
| `cy.contains(sel, text)` | `page.locator(sel).filter(has_text=text)` or `get_by_text` | |
| `.type(text)` | `.fill(text)` | Playwright doesn't need `.clear()` first — `fill` already replaces |
| `.selectFile(path)` | `.set_input_files(path)` | |
| `.should('be.visible')` | `expect(locator).to_be_visible()` | `playwright.sync_api.expect`, with built-in auto-retry |
| `cy.intercept()` + `cy.wait('@alias')` | `with page.expect_response(url_pattern) as resp_info:` | `with` block wrapping the action that triggers the request |
| `cy.origin('https://checkout.stripe.com', ...)` | nothing special — `page.wait_for_url("**checkout.stripe.com**")` | Playwright handles cross-origin natively |
| `cy.fixture('users.json')` | `json.load(open("test_data/users.json"))` via a pytest fixture | |
| Page Objects (JS classes, `export default new X()`) | Python classes receiving `page: Page` in `__init__` | instantiated via a pytest fixture (`@pytest.fixture def login_page(page): return LoginPage(page)`) |
| `element.validity.valid` / `validationMessage` | `locator.evaluate("el => el.validity.valid")` | same approach, via `evaluate` |
| Gherkin tags (`@crud @product @happy-path`) | pytest marks via pytest-bdd (`pytest.mark.crud` etc.) | enables `pytest -m happy_path` |
| `multiple-cucumber-html-reporter` | `pytest-html` (Phase 6) or `allure-pytest-bdd` (stretch) | see Phase 6 |
| `cypress-io/github-action` | `astral-sh/setup-uv` + `playwright install --with-deps` | see Phase 7 |

## 5. Phases

### Phase 0 — Project scaffolding
- [x] `uv init`, `pyproject.toml` with Python ≥ 3.11
- [x] Dependencies: `pytest`, `pytest-bdd`, `pytest-playwright`, `playwright`
- [x] `uv run playwright install --with-deps chromium`
- [x] Directory structure (section 3), updated `.gitignore` (`.venv/`, `__pycache__/`, `test-results/`, `playwright-report/`)
- [x] `conftest.py` with a `base_url` fixture (`https://wde-5p3f.onrender.com`)

**Done when:** `uv run pytest --collect-only` runs with no errors (even with no tests yet).

### Phase 1 — Core infrastructure (data + Page Objects)
- [x] Port `users.json`, `orders.json`, `mousepad.jpg` → `test_data/`
- [x] Port `helpers.js` → `utils/helpers.py` (`format_product_data`)
- [x] Python Page Objects: `LoginPage`, `ProductsPage`, `CartPage`, `OrdersPage`
- [x] Role-parameterized login fixture (`admin`/`customer`), equivalent to `commonSteps.js`

**Done when:** Page Objects have manual smoke coverage (a scratch script or a single login test).

### Phase 2 — Login and security (admin)
- [x] `login.feature`, `authentication.feature`, `authorization.feature`
- [x] `test_admin_login_steps.py`, `test_security_steps.py`, `test_common_steps.py`
- [x] Confirm the 2 known bugs (`BUG-AUTH-001`, `BUG-AUTH-002`) still reproduce the same way (same "must fail" scenarios)

**Done when:** the scenarios run against the deployed app and the result (pass/fail) matches the behavior documented in the bug reports.

### Phase 3 — Product CRUD (admin)
- [x] `manage_product.feature` + `test_manage_product_steps.py`
- [x] `fillProductForm` → Python method on `ProductsPage` (same field map as the original)
- [x] Required field validation via `validity`/`validationMessage`

**Done when:** all 4 scenarios (add, edit, delete, validation) pass end to end.

### Phase 4 — Order management (admin)
- [x] `manage_orders.feature` + `test_manage_orders_steps.py`
- [x] Swap `cy.intercept`/`cy.wait` for `page.expect_response`

**Done when:** a status update reflects in the badge, waiting for the real network response (not a `sleep`).

### Phase 5 — Customer purchase flow (E2E + Stripe)
- [x] `purchase_flow.feature` + `test_purchase_flow_steps.py`
- [x] Reproduce current behavior (stop at confirming the redirect to Stripe's domain)
- [x] Record as a "stretch" (Phase 9) the possibility of going further, since Playwright handles iframes/cross-origin better

**Done when:** the scenario passes and generates the same test order that today allows manually validating `BUG-AUTH-002`.

### Phase 6 — Reports and failure artifacts
- [x] Choose between `pytest-html` (simple) or `allure-pytest-bdd` (visual, closer to the current Cucumber HTML report) — suggestion: start with `pytest-html`, migrate to Allure if something more "portfolio-ready" is wanted
- [x] Configure `--tracing=retain-on-failure --video=retain-on-failure --screenshot=only-on-failure` (equivalent to Cypress's `video: true`, but only retained on failure)

**Done when:** a deliberate failure generates a recoverable trace/video/screenshot locally.

### Phase 7 — CI/CD (GitHub Actions)
- [x] New `playwright-tests.yml` workflow: Python + `uv` setup, `uv sync`, `playwright install --with-deps`
- [x] Keep the same strategic CI exclusion (no `purchase_flow` or `manage_orders` in the standard pipeline, same reason: avoid persistent data)
- [x] Artifact upload (`playwright-report/`, `test-results/`)
- [x] Update the README badge

**Done when:** a test PR triggers the workflow and the report artifact is available on Actions.

### Phase 8 — Documentation and cleanup
- [x] Rewrite `README.md` (stack, structure, install via `uv sync`, run via `uv run pytest`)
- [x] Keep `docs/bugs/` and `evidence/` (still valid, just update command references if they mention Cypress)
- [x] Before removing `cypress/`, `cypress.config.js`, `generate-cucumber-report.js`, `cucumber-messages.ndjson`: create a `legacy-cypress` tag/branch to preserve searchable history

**Done when:** the README only reflects the new stack, and the old Cypress suite is preserved on `legacy-cypress` but out of the main directory.

### Phase 9 — Improvements enabled by Playwright (stretch, post-parity)
- [x] Multi-browser matrix (chromium/firefox/webkit) in CI — Cypress only ran Chrome today. Finding: Firefox and WebKit spawn heavier processes than Chromium and had intermittent timeouts at `-n 4`; `-n 2` was reliable for both. Also exposed a test with hardcoded HTML5 validation text for Chromium's specific wording (`"Please fill out this field."`) — WebKit uses `"Fill out this field"`; fixed to check `validity.valueMissing` + a non-empty message, without pinning the exact text.
- [x] Parallel execution via `pytest-xdist` — `--dist=loadgroup` (pyproject.toml) + the `@xdist_group_product_crud` tag on the first 3 scenarios of `manage_product.feature`, mapped to `pytest.mark.xdist_group(name="product_crud")` via the `pytest_bdd_apply_tag` hook in `conftest.py`. Finding: `-n auto` (all cores) causes intermittent timeouts against the local app (a single Node/Mongo process, no scaling) — `-n 4` is the recommended ceiling, validated across multiple clean runs. Also exposed and fixed 3 unscoped locators (`Manage Products`/`Manage Orders`/`Logout`/`Orders` matched both the header and the mobile menu) that only turned into flakiness under concurrency.
- [x] Attempt to complete the Stripe test checkout (test card `4242...`) since Playwright handles cross-origin iframes better — done. Finding: the hosted Stripe page's (`checkout.stripe.com`) card fields render in the main document, not a cross-origin iframe, so `frame_locator` wasn't even needed. Confirmed working across all 3 matrix browsers; the hCaptcha present on the page didn't block automation with the test card.
- [x] Visual regression tests — Finding: `expect(page).to_have_screenshot()` **doesn't exist** in Playwright's Python API (only in the JS/TS test runner, the same class of gap already seen with "UI mode"); confirmed via an exhaustive grep of `_assertions.py`/`_generated.py`. Adopted `pytest-playwright-visual-snapshot` (the `assert_snapshot` fixture) as the equivalent. 5 pages covered in `features/visual/visual_regression.feature`: login, catalog, product details, admin/manage products, 401 error. Finding 2: the plugin embeds `sys.platform` in the snapshot name — baselines generated on Windows would never match CI's `ubuntu-latest`; baselines were generated by running the suite inside the official `mcr.microsoft.com/playwright/python` image (same Ubuntu Noble base as the runner), connected to the app's Docker network (`wde_default`). Finding 3: Compose's `app` hostname triggers Chromium's HSTS preload for the `.app` gTLD, forcing HTTPS and breaking `http://app:3000` — worked around by pointing at the container's real name (`wde-app-1`). Visual tests stay out of the standard local suite (`-m "not visual"` in `addopts`) and only run in CI via `-m visual`, since they depend on a Linux baseline.
- [x] Lightweight API coverage with `playwright.request` — done as part of the advanced security suite: the `BUG-SEC-005` scenario uses `playwright.request.new_context()` to send only the forged cookie (no real browser session) and validate the direct HTTP response from `GET /admin/products`.

## 6. Risks / points of attention

- **Language change = zero code reuse**, only structure/logic reuse. Every step had to be rewritten, not just translated 1:1.
- **The target app is a free Render deployment** (`wde-5p3f.onrender.com`) — may hibernate/cold-start; consider a longer `timeout` on each CI session's first `goto`. (Superseded — see Phase 10: the app now runs locally via Docker.)
- **`manage_orders.feature` depends on a fixed `testOrderId`** (`orders.json`) — if that order is removed/changed in the app's database, the scenario breaks independent of the migration.
- **Authorization bugs are this portfolio's "product"** — any security step needs extra-careful validation so as not to accidentally mask the real bug while rewriting it.

## 7. Immediate next step (historical)

Start with **Phase 0** (scaffolding) once this roadmap is approved.

---

## Phase 10 — i18n, catalog overhaul, feature expansion & email integration

Full plan approved via `/plan` on 2026-07-29 (see conversation history / plan artifact for the complete rationale). Summary:

### Context

Two more goals surfaced after Phase 9 wrapped up:
1. Make the project read as English-first (the user now works internationally). This repository (`wde_automacao`) was ~100% Portuguese (feature files, docs, step-matcher strings) — the `wde` app itself was already 100% English code/UI.
2. Expand `wde` itself, inspired by the darkartswizard.com "Automation Tools Checklist", covering UI element patterns the app doesn't exercise yet, a real product catalog (today only 3 products), and email-based flows (order confirmation, OTP login).

Key decisions:
- Stay on **Python** for the test suite (evaluated switching to TypeScript; nothing in the new scope — Mailpit's HTTP API, OTP, catalog filter/sort, i18n — needs a JS/TS-exclusive Playwright feature).
- Add a real **bilingual language selector** to `wde` (English default, Portuguese-BR toggle), hand-rolled (no `i18next`) given the app's existing no-bundler, vanilla-JS/EJS convention.
- Catalog images: **generated placeholders**, not stock photos (no licensing risk, no external network dependency during seeding).
- Email testing via **Mailpit** (local SMTP catcher + REST API), read back in tests via `playwright.request` — the same pattern already proven in the `BUG-SEC-005` PoC.

### Tracks

- [x] **Track 1** — Convert `wde_automacao` to English (this document, `README.md`, `docs/bugs/*.md`, every `.feature` file, step-matcher strings, comments, the `"cliente"` → `"customer"` role key).
- [x] **Track 2** — `wde`: i18n infrastructure, language selector, localized product catalog copy.
- [x] **Track 3** — `wde_automacao`: language-selector scenarios. `features/localization/language_selector.feature` — a `Scenario Outline`/`Examples` (a first for this suite) covering both EN and PT nav-label switching, plus a separate scenario proving product *content* (not just nav chrome) is localized. A `set_language` factory fixture (mirrors `login_as`) backs a reusable `Given the language is set to "..."` step for future scenarios that need a language precondition. Runs as its own chromium-only CI step (no browser-specific rendering risk, so no need to triple it across the matrix).
- [x] **Track 4** — Catalog overhaul, sub-phased deliberately slowly:
  - [x] 4a. `department` field + a meaningfully larger seed catalog with generated placeholder thumbnails. Went from 3 to 24 products across 6 departments (Electronics, Gaming, Furniture, Office, Home, Sports); the 21 new products get deterministic SVG placeholders (product name + department-coded color, generated at seed time, no external image fetch/licensing risk). Also added the `department` select to the admin product form itself — a schema field with no way to set it via the app's own CRUD UI would have been a real gap, not just deferred UI polish. Caught and fixed a bug before it shipped: `docker-compose.yml`'s `seed` service was missing the same bind mount `app` has for `product-data/images/`, so generated placeholders were written into the seed container's ephemeral filesystem and silently lost on every run - added the same volume mount to `seed`.
  - [x] 4b. Backend filter/sort (`?department=&sort=`) — `Product.findAll({department, sort})` + `products.controller.js` reading the query string, guarded the same way the login/signup NoSQL injection fix was (only plain-string query values reach the Mongo filter, since Express parses `?department[$ne]=null` into a nested object otherwise). Also added price display to the shared `product-item.ejs` card, previously only shown on the product detail page - needed to verify price sort visually/in tests, and was an overdue gap now that the catalog is a real size. `features/catalog/catalog_filter_sort.feature` verifies department filtering (checked against MongoDB directly, not a second hardcoded product list) and both sort directions for name and price.
  - [x] 4c. Frontend filter/sort UI — department `<select>` + sort `<select>` above the catalog grid, plain `GET` form submit (no JS) - the checklist's "List : select" pattern. Both selects are fully localized (labels, department names, sort option text) while their `value` attributes stay canonical English, so behavior doesn't depend on active language. Verified via both direct-URL scenarios (Track 4b) and genuine dropdown-selection scenarios (Track 4c) in the same feature file. Surfaced a pytest-bdd scoping gap along the way: step definitions in one `steps/*.py` file aren't visible to another - only `steps/conftest.py` steps are shared across files (same as pytest fixture scoping) - moved the shared "Given I am on the product catalog" step there.
  - [x] 4d. Live search / combobox — `GET /api/products/search?q=` (debounced, plain vanilla JS, no framework) matches against both the canonical title and every stored translation's title, so search works regardless of which language the shopper types in. User-supplied query text is escaped before being used as a Mongo `RegExp` (same discipline as 4b's filter guard - raw user input into a regex is its own injection/ReDoS class). Covers the checklist's "API JSON: Response Key:Value" pattern directly via a `playwright.request` scenario asserting on the JSON body, plus UI-driven scenarios for typing/suggestions/navigation.
- [x] **Track 5** — Remaining targeted UI-pattern features:
  - [x] 5a. Confirmation modal (product delete) — native `<dialog>` + `showModal()`, not a hand-rolled overlay: the browser makes background content genuinely inert natively (no `inert`/focus-trap code needed), which is what the checklist's "Disabled Under Modal" pattern actually requires - verified by attempting to click a background link while the dialog is open and confirming it doesn't navigate. Replaces the old confirm-less immediate delete in `product-management.js`. Two new scenarios: confirming deletes, cancelling doesn't (and the product is still there afterward) - both run cross-browser (Chromium/Firefox/WebKit) since `<dialog>` is newer API surface worth checking explicitly.
  - [x] 5b. Toast notifications — hand-rolled `public/scripts/toast.js` (no library) replaces every `alert()` in `cart-management.js`/`cart-item-management.js`/`product-management.js`/`order-management.js`, plus new success toasts on the happy paths. Auto-dismiss uses a second fixed `setTimeout`, not a `transitionend` listener - that event doesn't reliably fire when a tab isn't actively compositing (backgrounded/inactive tabs, some automated browser contexts), which would have left toasts stuck in the DOM forever; found this empirically while manually verifying the feature, not in automated tests. Also found and fixed a real pre-existing bug while wiring this up: `admin-orders.ejs` never included the shared `footer.ejs` (a bare `</body>` with no `</html>` at all), so the new toast container never rendered there - every other view already included it correctly.
  - [x] 5c. Sortable admin orders table — `admin-orders.ejs` moved from a card list to a real `<table>` (admin-only; the customer's own-orders view stays as cards, kept as a separate template since the DOM structures diverge too much to share). Click-to-sort via a small vanilla-JS script (`order-table-sort.js`) reading `data-*` attributes on each row - no server round-trip. Verified cross-browser (Chromium/Firefox/WebKit). Test assertion reads the actual `data-*` values and checks sortedness generically, rather than asserting a specific row count/order, so it holds regardless of how many orders exist in a given environment (1 on a fresh CI run vs. many after repeated local `purchase_flow` runs).
  - [x] 5d. Date picker (product `launchDate`) — self-hosted flatpickr v4.6.13 (`public/scripts/vendor/`, `public/styles/vendor/`) on the admin product form; a native `<input type="date">` was deliberately avoided since native date pickers are notoriously inconsistent to automate across browser engines, while flatpickr renders a real, locatable calendar (`.flatpickr-day[aria-label="..."]`) that Playwright can click directly. Customer-facing product detail page conditionally shows "Available since {date}" when a product has one set. Found and fixed a real bug in the page object while extending the CRUD scenario to a fresh product instead of the seeded chair (see below): flatpickr opens showing *today's* month when the input starts empty, not the month of any date you're about to pick, so `set_launch_date()` now explicitly drives the picker's month `<select>` and year spinbutton to the target date before clicking the day cell, rather than assuming the target day is already visible on open. Also caught and reverted a shared-fixture mutation before it reached CI: the first draft of this scenario set the launch date directly on the persistent seeded "GTRACING - Black Gaming Chair" (relied on by the product-details visual regression baseline and other scenarios), which silently changed its expected date for every later test run; folded the launch-date step into the existing disposable "Successfully edit an existing product" mousepad scenario instead, consistent with the project's practice of not mutating shared seed data. Verified cross-browser (Chromium/Firefox).
  - [x] 5e. Drag-and-drop product image upload — the existing `<input type="file">` + `image-preview.js` dropzone (`#image-upload-control`) gained `dragover`/`dragleave`/`drop` handlers; on drop, `event.dataTransfer.files` (a real `FileList`) is assigned directly to the input's own `.files` property and a synthetic `change` event fires, so the existing preview code and the unchanged multer backend both keep working without knowing whether the file arrived via click-to-browse or drag-and-drop. No backend change needed - same `upload.single('image')` field. Playwright has no built-in "drop a file" helper (unlike `set_input_files` for the native picker), so `drop_image_file()` builds a real `File` from the fixture's bytes inside `page.evaluate` and dispatches a native `DragEvent('drop', { dataTransfer })` at the dropzone element - verified this actually exercises the same code path as a real OS-level drag by checking `dragover`/`drop` update the input's `.files` and preview in the browser first, manually, before automating it. New disposable CRUD scenario (own product, cleaned up via delete) rather than reusing/mutating any other scenario's data. Verified cross-browser (Chromium/Firefox/WebKit).
  - [x] 5f. Rich text editor for product description — self-hosted Quill 1.3.7 (`public/scripts/vendor/`, `public/styles/vendor/`) on the admin form, replacing the plain `<textarea>`; a hidden `<textarea id="description">` stays in sync via a `text-change` listener (plus a submit-time sync as a backstop) so the existing multer/form-submission plumbing is untouched. The critical piece is server-side: `utils/sanitizeDescription.js` runs `sanitize-html` against an explicit allowlist matching only what the toolbar can actually produce (bold/italic/underline/strike/lists/blockquote/links), applied in `admin.controller.js` on both create and update - switching the customer-facing render from `<%= %>` to `<%- %>` (raw HTML) without this would have been a straightforward stored-XSS hole. Verified the boundary two ways: directly at the sanitizer function (script tags, `onerror` handlers, and `javascript:` URLs are stripped while safe formatting and links survive) and end-to-end via a new Playwright scenario that bypasses the Quill toolbar entirely (`page.evaluate` writing raw HTML straight into the editor's DOM, dispatching a real `input` event) to reach the server with a payload the UI itself would never produce - the same realistic threat model as a modified client or direct API call. Along the way, found that `product-item.ejs`'s "View Details" link only renders for non-admin viewers (`locals.isAdmin` branches to "View & Edit"/"Delete" instead), so verifying the customer-facing render required navigating directly to `/products/:id` using the id lifted from the admin edit link, not clicking a button that doesn't exist on that page. Verified cross-browser (Chromium/Firefox/WebKit).
  - [x] 5g. PDF invoice download — `GET /orders/:id/invoice.pdf` streams a `pdfkit`-generated PDF (pure-JS, no native compilation needed, safe for the `node:20-alpine` image), gated by the same ownership check pattern as the rest of the orders routes (`order.userData._id` must match `res.locals.uid`, else a 404 - not a 403, so the route doesn't confirm to a caller whether an order id merely belongs to someone else vs. doesn't exist at all). Order data is normalized once by a new `utils/orderSummary.js`, kept deliberately free of any `pdfkit` import so it can be reused as-is by Track 6b's confirmation email without pulling a PDF-rendering dependency into the email path; `utils/invoicePdf.js` is the only module that knows about `pdfkit` layout. Found and fixed a real pre-existing gap while wiring this up: `Order.findById` never handled a not-found id (unlike `Product.findById`, which already 404s cleanly) - a bad/guessed order id crashed with an uncaught `TypeError` (500) instead of a clean 404, since this route is the first thing to expose `Order.findById` to a directly user-controlled id. Brought it in line with `Product.findById`'s existing pattern. Verified manually (real PDF bytes, correct `Content-Type`/`Content-Disposition`, ownership check, both the "nonexistent id" and "malformed id" cases now 404) before automating; the download link only renders for customers in `order-item.ejs` (`!locals.isAdmin`), since the route's ownership check would 404 for an admin viewing someone else's order anyway.
- [x] **Track 6** — Email integration: Mailpit infra, order confirmation email, additive OTP login flow.
  - [x] 6a. Mailpit infra — `axllent/mailpit` added as a new `docker-compose.yml` service (SMTP `:1025`, HTTP API `:8025`), `nodemailer` wired via a new `config/mailer.js` transporter reading `SMTP_HOST`/`SMTP_PORT` from env, matching the existing `config/session.js` config-factory convention. No third-party account/API key needed. Verified manually end-to-end before writing any automated coverage: sent a real test email through the transporter, confirmed it landed in Mailpit's web UI, and confirmed Mailpit's `GET /api/v1/messages` REST API (what Track 6b's tests will read from) returns it too. This track is infra only - nothing in the app actually sends an email yet; that's Track 6b. Also updated the CI workflow's generated `.env` for the app stack to include the same SMTP env vars, since the compose file change alone doesn't help if the env vars pointing at it are missing - otherwise Track 6b's email send would fail against `undefined:NaN` in CI.
  - [x] 6b. Order confirmation email — sent from the existing `/orders/success` redirect handler rather than a Stripe webhook, matching the app's current no-webhook architecture (no `stripe listen` operational complexity added). The order is saved (and its real DB id captured) *before* the Stripe session is created, so that id now rides along in `success_url` as `?orderId=...` - `getSuccess` reads it back, re-checks ownership the same way the invoice route does, and sends the confirmation through `utils/orderConfirmationEmail.js`, which reuses Track 5g's `utils/orderSummary.js` unchanged (the reason that module was kept free of any `pdfkit` import). The email send is deliberately best-effort: wrapped in try/catch inside `getSuccess` so a bad/missing order id or a transient SMTP hiccup never blocks the success page itself - checkout completing shouldn't depend on mail delivery. Verified with a real end-to-end purchase (test Stripe card, real checkout, real redirect) before automating: confirmed the email actually lands in Mailpit with the correct customer name, order id, line items and total. Automated coverage extends the existing "Customer successfully purchases a specific product" scenario (rather than adding a second full checkout scenario) with a step that polls Mailpit's `GET /api/v1/messages` via `playwright.request` - same isolated-request-context pattern as the `BUG-SEC-005` PoC - matching on both the order id (parsed from the success page's URL) and the recipient address, with a short poll since Mailpit indexes messages asynchronously over real SMTP. Verified cross-browser (Chromium/Firefox/WebKit) - note this had to be run directly on the host via `uv run pytest`, not nested inside the Linux Docker image used for other manual checks this session, since the Stripe redirect back to `APP_URL` only resolves correctly when the browser and the app share the same network namespace as whatever `APP_URL` points to.
  - [x] 6c. OTP login flow — additive, not a replacement: a new "Login with an email code instead" link on the existing password login page leads to `GET /login/otp` (email entry) → `GET /login/otp/verify` (6-digit code entry), backed by a new `Otp` collection/model (`models/otp.model.js`) with a 10-minute expiry and a 5-attempt limit per code, generated with Node's `crypto.randomInt` (not `Math.random()` - it's an authentication factor, not a filename suffix, so it gets the same randomness discipline as anything else security-relevant in this app). Every existing password-login scenario is untouched. Mirrors the app's existing user-enumeration protection on the password login path (which already returns the identical "Invalid Credentials" response whether the account doesn't exist or the password is merely wrong): requesting a code redirects to the same verify page regardless of whether the email is registered, and only actually creates a code/sends an email for accounts that exist - verified directly against the database that a nonexistent email produces zero `otps` documents and zero attempts to send mail. The 5-attempt limit was verified as a real lockout, not just a UI message: after 5 wrong submissions the `otps` document is deleted server-side, so even the *correct* code is then rejected and no session gets created - this is what the paired Playwright scenario below is really testing (an account-lockout-prevention check in the same spirit as the app's other security scenarios), not merely "wrong code shows an error." Automated coverage retrieves the real code from Mailpit via `playwright.request` (same pattern as Track 6b), fetching the full message body through `GET /api/v1/message/{ID}` rather than trusting the summary list's `Snippet` to necessarily contain the whole 6-digit code. Verified cross-browser (Chromium/Firefox/WebKit); confirmed the existing admin-login and security-hardening suites are unaffected by the changes to `auth.controller.js`/`login.ejs`.
- [x] **Track 7** — Docs/CI wrap-up across both repos: this section (top-level track checkboxes were left stale after each track's own commit - fixed here), the CI workflow's core-suite file list, and both READMEs (`wde`'s was still 100% Portuguese - the one piece of the original "make the project read as English-first" goal that hadn't been touched by any earlier track, since Track 1 only covered this repository). `steps/test_catalog_filter_sort_steps.py`, `steps/test_otp_login_steps.py`, and `steps/test_order_invoice_steps.py` are now part of `playwright-tests.yml`'s explicit core-suite run (verified locally first with the exact CI invocation - `-n 4`, same file list - before pushing: 28 passed, 8 xfailed, 0 failures). `manage_orders.feature` and `purchase_flow.feature` stay excluded, unchanged from the original Cypress-era rationale: both create persistent orders in the database on every run, which the other three newly-added files don't (OTP records self-delete on success or lockout; the invoice scenarios only read existing orders; catalog scenarios only filter/search).

Each track/sub-phase is reviewed, committed, pushed, and CI-verified before moving to the next — same workflow as Phase 9.

### Phase 10 wrap-up

All seven tracks are complete and CI-green on both repos as of this section. What Phase 10 actually delivered, end to end:

- **Localization**: `wde_automacao` fully converted to English (Track 1); `wde` gained a hand-rolled i18n layer, an EN/PT-BR language selector, and localized product content (Track 2), verified by a dedicated `Scenario Outline` suite (Track 3).
- **Catalog**: went from 3 products to 24 across 6 departments, with department/sort filtering, a live search combobox, and a JSON search API (Track 4a-4d).
- **UI-pattern coverage**: confirmation modal, toast notifications, a sortable admin orders table, a self-hosted date picker, drag-and-drop image upload, a self-hosted rich text editor (with a real stored-XSS defense, not just a UI nicety), and PDF invoice download (Track 5a-5g).
- **Email integration**: a local Mailpit stack, real order confirmation emails sent from the checkout success handler, and an additive OTP login flow with a genuine server-side lockout after repeated wrong attempts (Track 6a-6c).
- **Two real, unrelated bugs found and fixed along the way**, not part of any track's original scope: `admin-orders.ejs` was missing the shared footer include entirely (silently broke the new toast container - Track 5b), and `Order.findById` never handled a not-found document, 500ing instead of 404ing on a bad order id once a customer-facing route started exposing it to user-controlled input (Track 5g).
- **Everything landed with cross-browser verification** (Chromium/Firefox/WebKit) wherever the feature wasn't inherently platform/rendering-specific, real manual verification of every email/PDF/security-sensitive flow before automating it, and no track's automated coverage relied on mutating shared seed data - each new scenario either used its own disposable data or explicitly reverted anything it touched on persistent fixtures.
