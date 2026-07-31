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
- [ ] **Track 2** — `wde`: i18n infrastructure, language selector, localized product catalog copy.
- [x] **Track 3** — `wde_automacao`: language-selector scenarios. `features/localization/language_selector.feature` — a `Scenario Outline`/`Examples` (a first for this suite) covering both EN and PT nav-label switching, plus a separate scenario proving product *content* (not just nav chrome) is localized. A `set_language` factory fixture (mirrors `login_as`) backs a reusable `Given the language is set to "..."` step for future scenarios that need a language precondition. Runs as its own chromium-only CI step (no browser-specific rendering risk, so no need to triple it across the matrix).
- [ ] **Track 4** — Catalog overhaul, sub-phased deliberately slowly:
  - [x] 4a. `department` field + a meaningfully larger seed catalog with generated placeholder thumbnails. Went from 3 to 24 products across 6 departments (Electronics, Gaming, Furniture, Office, Home, Sports); the 21 new products get deterministic SVG placeholders (product name + department-coded color, generated at seed time, no external image fetch/licensing risk). Also added the `department` select to the admin product form itself — a schema field with no way to set it via the app's own CRUD UI would have been a real gap, not just deferred UI polish. Caught and fixed a bug before it shipped: `docker-compose.yml`'s `seed` service was missing the same bind mount `app` has for `product-data/images/`, so generated placeholders were written into the seed container's ephemeral filesystem and silently lost on every run - added the same volume mount to `seed`.
  - [x] 4b. Backend filter/sort (`?department=&sort=`) — `Product.findAll({department, sort})` + `products.controller.js` reading the query string, guarded the same way the login/signup NoSQL injection fix was (only plain-string query values reach the Mongo filter, since Express parses `?department[$ne]=null` into a nested object otherwise). Also added price display to the shared `product-item.ejs` card, previously only shown on the product detail page - needed to verify price sort visually/in tests, and was an overdue gap now that the catalog is a real size. `features/catalog/catalog_filter_sort.feature` verifies department filtering (checked against MongoDB directly, not a second hardcoded product list) and both sort directions for name and price.
  - [x] 4c. Frontend filter/sort UI — department `<select>` + sort `<select>` above the catalog grid, plain `GET` form submit (no JS) - the checklist's "List : select" pattern. Both selects are fully localized (labels, department names, sort option text) while their `value` attributes stay canonical English, so behavior doesn't depend on active language. Verified via both direct-URL scenarios (Track 4b) and genuine dropdown-selection scenarios (Track 4c) in the same feature file. Surfaced a pytest-bdd scoping gap along the way: step definitions in one `steps/*.py` file aren't visible to another - only `steps/conftest.py` steps are shared across files (same as pytest fixture scoping) - moved the shared "Given I am on the product catalog" step there.
  - [ ] 4d. Live search / combobox (`GET /api/products/search`)
- [ ] **Track 5** — Remaining targeted UI-pattern features: confirmation modal, toast notifications, sortable admin orders table, date picker, drag-and-drop image upload, rich text editor for product description, PDF invoice download.
- [ ] **Track 6** — Email integration: Mailpit infra, order confirmation email, additive OTP login flow.
- [ ] **Track 7** — Docs/CI wrap-up across both repos.

Each track/sub-phase is reviewed, committed, pushed, and CI-verified before moving to the next — same workflow as Phase 9.
