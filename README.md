# Test Automation (QA Portfolio) - WDE Shop

![CI Status](https://github.com/Gabriel-Leao51/wde-test-automation/actions/workflows/playwright-tests.yml/badge.svg)

## 1. Introduction

This repository contains an E2E (End-to-End) test automation project built as part of a Quality Assurance (QA) portfolio. The main goal was to build a robust test suite using modern technologies and industry best practices, demonstrating skills in automation, BDD, CI/CD, and bug discovery.

The application under test (AUT) is **WDE Shop** ([repository](https://github.com/Gabriel-Leao51/wde)), running locally via Docker Compose (app + MongoDB), replacing the previously Render-hosted deployment.

> This project started as a **Cypress + Cucumber (JavaScript)** suite and was migrated to **Playwright + pytest-bdd (Python)**. The original Cypress suite remains preserved and browsable on the [`legacy-cypress`](https://github.com/Gabriel-Leao51/wde-test-automation/tree/legacy-cypress) branch. Migration details (decisions, phases, Cypress → Playwright mapping) are in [ROADMAP.md](ROADMAP.md).

## 2. Automation Scope

The project covers different testing areas and types:

- **Functional Tests (Admin Panel):**
  - **Login:** Admin panel authentication.
  - **Product Management:** Full CRUD (Add, Edit, Delete) - Happy Path.
  - **Product Management:** Required field validation (Name/Title) - Unhappy Path.
  - **Order Management:** Changing an existing order's status.
- **Security Tests (Admin Panel):**
  - **Authentication:** Attempts to access admin areas by unauthenticated users.
  - **Authorization:** Attempts to access admin areas by logged-in users with a "customer" profile (unauthorized).
- **E2E Test (Customer Flow):**
  - **Purchase Journey:** Customer login, product search, adding to cart, checkout, filling in the test card on Stripe's page, and confirmation through to the order success page.
- **Visual Regression:**
  - Screenshot vs. approved baseline comparison across 5 key pages: login, product catalog, product details, admin product panel, and the 401 error page.

## 3. Technologies and Methodologies Used

- **Automation Framework:** [Playwright](https://playwright.dev/python/) (Python, sync API)
- **Language:** Python 3.12
- **BDD Approach:** Gherkin (English) via [pytest-bdd](https://pytest-bdd.readthedocs.io/)
- **Design Pattern:** Page Object Model (POM)
- **Package Manager:** [uv](https://docs.astral.sh/uv/)
- **CI/CD:** GitHub Actions
- **Reporting:** `pytest-html` (self-contained HTML report), Playwright trace/video/screenshot retained on failure
- **Visual Regression:** [`pytest-playwright-visual-snapshot`](https://pypi.org/project/pytest-playwright-visual-snapshot/) (the Python equivalent of `to_have_screenshot()`, which only exists in the JS/TS test runner)
- **Data Management:** JSON fixtures (`test_data/`) for users and orders, test image for upload
- **Local target application:** Docker Compose ([`wde` repository](https://github.com/Gabriel-Leao51/wde)) — app + MongoDB, with automatic data seeding
- **Version Control:** Git / GitHub

## 4. Project Structure

```
.
├── pyproject.toml              # Dependencies and pytest configuration (uv)
├── uv.lock
├── conftest.py                 # base_url, Page Object fixtures, and login
├── features/
│   ├── admin/                  # Login, authentication, authorization, products, orders features
│   ├── client/                 # Purchase flow feature
│   ├── security/                # Advanced security features (hardening)
│   └── visual/                  # Visual regression feature
├── steps/                      # Step definitions (pytest-bdd) + conftest.py with shared steps
├── pages/                      # Page Objects (LoginPage, ProductsPage, CartPage, OrdersPage, StripeCheckoutPage)
├── __snapshots__/              # Visual regression baselines (generated on Linux — see section 7.9)
├── test_data/                  # Data fixtures (users.json, orders.json, mousepad.jpg)
├── utils/                      # Helper functions (helpers.py)
├── docs/bugs/                  # Reports for bugs found
├── evidence/                   # Screenshots and videos proving the unexpected behavior
├── .github/workflows/
│   └── playwright-tests.yml
└── ROADMAP.md                  # Roadmap and history of the Cypress → Playwright migration
```

## 5. Prerequisites

- [Python](https://www.python.org/) 3.12+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (to run the target application locally)
- [Git](https://git-scm.com/)

## 6. Installation

1. Clone both repositories (the target application and the test suite):

   ```bash
   git clone https://github.com/Gabriel-Leao51/wde.git
   git clone https://github.com/Gabriel-Leao51/wde-test-automation.git
   ```

2. Bring up the WDE Shop application locally (see the [`wde` repository README](https://github.com/Gabriel-Leao51/wde#-rodando-localmente-com-docker) for details — in short: `cp .env.example .env`, fill in `STRIPE_KEY`, and `docker compose up --build`). The application comes up at `http://localhost:3000`, already populated with test data by the seed script.

3. Install the test suite's dependencies:

   ```bash
   cd wde-test-automation
   uv sync
   uv run playwright install --with-deps chromium
   ```

## 7. Running Tests

### 7.1. Full suite

```bash
uv run pytest
```

Runs on Chromium by default. To run on another browser:

```bash
uv run pytest --browser=firefox
uv run pytest --browser=webkit
```

### 7.2. Headed mode (with a visible browser)

```bash
uv run pytest --headed
```

Add `--slowmo=400` (value in ms) to slow down actions and make visual observation easier.

### 7.3. A specific file

```bash
uv run pytest steps/test_manage_product_steps.py
```

### 7.4. Parallel execution

```bash
uv run pytest -n 4
```

Uses [`pytest-xdist`](https://pytest-xdist.readthedocs.io/). The first 3 scenarios of `manage_product.feature` (add, edit, delete) are interdependent — they operate on the same product in sequence — so they carry the `@xdist_group_product_crud` tag, which pins them to the same worker (via `--dist=loadgroup`, already configured in `pyproject.toml`, and the `pytest_bdd_apply_tag` hook in `conftest.py`). The 4th scenario (required field validation) is independent and doesn't need the tag. The rest of the suite parallelizes freely across the remaining workers.

`-n 4` is a deliberate ceiling, not `-n auto`: WDE Shop runs as a single Node/Express process + a single MongoDB instance, with no scaling. In local testing, `-n auto` (using all machine cores) produced intermittent timeout failures under load — the app simply doesn't respond fast enough with many concurrent sessions. `-n 4` ran consistently across multiple runs.

### 7.6. Pointing at a different environment

By default the suite targets `http://localhost:3000`. To run against a different URL:

```bash
WDE_BASE_URL=http://other-host:3000 uv run pytest
```

### 7.7. Reports and failure artifacts

Each run generates a self-contained HTML report at `playwright-report/report.html`. Failures automatically retain trace, video, and screenshot in `test-results/`, recoverable for local debugging:

```bash
uv run playwright show-trace test-results/<test-folder>/trace.zip
```

### 7.8. Advanced security suite (`features/security/`)

Besides the UI/HTTP tests (Playwright), the `BUG-SEC-005` proof-of-concept scenario connects directly to MongoDB to forge a session (see the bug report for details). Because of this, the `wde` repository's `docker-compose.yml` publishes MongoDB's port at `127.0.0.1:27017`. If you're running tests outside the local default (`localhost:3000` + `localhost:27017`), also point the `MONGODB_URI` variable:

```bash
MONGODB_URI=mongodb://other-host:27017 uv run pytest steps/test_security_hardening_steps.py
```

### 7.9. Visual regression (`features/visual/`)

The baselines in `__snapshots__/` were generated on **Linux** (the same Ubuntu Noble base as the CI's `ubuntu-latest` runner), because `pytest-playwright-visual-snapshot` writes the snapshot filename with a fixed value (we deliberately don't embed `sys.platform` — see ROADMAP, Phase 9). Font rendering/anti-aliasing differs between Windows and Linux, so running these tests locally on Windows would always report a difference, even with no real layout change. Because of this:

- **They're excluded from the local suite by default:** `addopts` already includes `-m "not visual"`, so `uv run pytest` (section 7.1) doesn't run them.
- **In CI**, they run explicitly via `-m visual`, Chromium only (to avoid tripling baseline maintenance across the matrix).
- **To run or update the baselines**, use Playwright's official image (same base as CI), connected to the application's Docker network:

  ```bash
  docker run --rm --network wde_default \
    -v "$(pwd):/work" -w /work \
    -e WDE_BASE_URL=http://wde-app-1:3000 \
    mcr.microsoft.com/playwright/python:v1.61.0-noble \
    bash -c "pip install --quiet pymongo pytest pytest-bdd pytest-html pytest-playwright pytest-xdist pytest-playwright-visual-snapshot && python -m pytest -m visual --browser chromium --update-snapshots steps/test_visual_regression_steps.py"
  ```

  Use `wde-app-1` (the container name, not `app`) as the host: Chromium forces HTTPS on any host literally named `app` via the `.app` gTLD's HSTS preload list, which breaks `http://app:3000`. Without `--update-snapshots`, the same command compares against the existing baseline.

## 8. Continuous Integration (CI/CD) with GitHub Actions

The workflow is configured in `.github/workflows/playwright-tests.yml` and performs the following steps:

- **Triggers:** Runs on `push` and `pull_request` events to the `main` branch.
- **Environment:** Ubuntu with Python 3.12 (via `uv`) and Docker.
- **Target application:** Checks out the `wde` repository as a sibling directory and brings up the stack via `docker compose up -d --build`, waiting for the health check before proceeding.
- **Multi-browser matrix:** runs the full job 3 times in parallel (Chromium, Firefox, WebKit), each with its own isolated Docker stack (avoids concurrency interference between browsers). `fail-fast: false` — a failure in one browser doesn't cancel the others.
- **Installation:** `uv sync` + `playwright install --with-deps <matrix-browser>`.
- **Running tests:** Runs the core subset (`login`, `authentication`, `authorization`, `manage_product`) in parallel via `pytest-xdist` (see section 7.4) — `-n 4` for Chromium, `-n 2` for Firefox/WebKit (heavier processes, had intermittent timeouts at `-n 4` during local validation). Just like in the original Cypress version, `manage_orders.feature` and `purchase_flow.feature` are left out of the standard pipeline — both create persistent orders in the database on every run, which is undesirable in a CI pipeline.
- **Visual regression:** runs as an extra step, only on the Chromium leg of the matrix (`-m visual`, see section 7.9), comparing against the Linux baselines versioned in `__snapshots__/`.
- **Known bugs as `@xfail`:** The 3 scenarios in `authorization.feature` documenting `BUG-AUTH-001`/`BUG-AUTH-002` are tagged `@xfail` (with `xfail_strict` enabled). This lets the pipeline report success normally while still running and tracking these scenarios — if either bug is fixed, the corresponding scenario turns into an `XPASS` and breaks the build, flagging the regression instead of it slipping by unnoticed.
- **Artifact Upload:** Makes the HTML report and failure artifacts (`playwright-report/`, `test-results/`) available as a build artifact in GitHub Actions.

(Link to the latest build status via the badge at the top of this README.)

## 9. Findings and Identified Bugs

During automation development, security vulnerabilities were identified in the WDE Shop application. The ones still present are reproduced by the current suite (marked `@xfail` so they don't break CI, but still run on every run in `features/security/hardening.feature` and `features/admin/authorization.feature`).

### Fixed

**NoSQL Injection → Full Application Crash (unauthenticated)**

Description: `POST /login` (or `/signup`) with a JSON body of `{"email":{"$ne":null},"password":{"$ne":null}}` made MongoDB interpret `$ne` as a query operator (bypassing the exact-email lookup) and then crashed the entire Node process by passing an object (instead of a string) to `bcrypt.compare()` — an unhandled exception. A single unauthenticated request was enough to take the application down for every user.

Fix: type validation (`email`/`password` must be strings) added in `controllers/auth.controller.js` and `util/validation.js`, closing both the injection vector and the crash.

Proof: `features/security/hardening.feature`, NoSQL injection scenarios against `/login` and `/signup` — now pass normally (no longer `@xfail`), validating that the application responds with "Invalid credentials" and stays up.

### Still present

**BUG-AUTH-001: Authorization Failure on Access to Admin Pages**

Description: Users authenticated with the "customer" profile can directly access product management URLs (`/admin/products`, `/admin/products/:id`), which should be restricted to administrators.

Proof: The automated scenarios in `authorization.feature` document the expected behavior (access denied) and intentionally fail against the actual behavior, confirming the vulnerability.

Detailed Report: [BUG-AUTH-001 Report](docs/bugs/BUG-AUTH-001.md)

**BUG-AUTH-002: Authorization Failure and Information Leak on the Orders Page**

Description: Users authenticated as "customer" can access the `/admin/orders` URL. Although the page appears partially broken (no admin controls), it displays order information, including other users' orders.

Proof: The automated scenario for `/admin/orders` doesn't produce the expected authorization message, and manual verification confirmed improper access to other users' data.

Detailed Report: [BUG-AUTH-002 Report](docs/bugs/BUG-AUTH-002.md)

**BUG-INFO-001: Exposure of Internal Server Details on Error Pages**

Description: `NODE_ENV` is never set to `production`, so any unhandled exception exposes server paths, template source-code snippets, and Node stack traces to the client. Made worse by a cascading failure: the error page itself (`500.ejs`) breaks trying to render `locals.cart`, which doesn't exist for errors raised before `cartMiddleware` runs (e.g. CSRF rejection).

Detailed Report: [BUG-INFO-001 Report](docs/bugs/BUG-INFO-001.md)

**BUG-SEC-002: Missing HTTP Security Headers**

Description: No standard security header (`Content-Security-Policy`, `X-Frame-Options`, `X-Content-Type-Options`, etc.) is present in responses, and `X-Powered-By: Express` leaks the technology stack. No security middleware (`helmet` or equivalent) is in use.

Detailed Report: [BUG-SEC-002 Report](docs/bugs/BUG-SEC-002.md)

**BUG-SEC-003: CSRF Token Exposed in the Product Form URL**

Description: The product form sends the CSRF token as a query-string parameter (`?_csrf=...`) in the `action`, instead of a hidden field — unlike every other form in the application, which does this correctly.

Detailed Report: [BUG-SEC-003 Report](docs/bugs/BUG-SEC-003.md)

**BUG-SEC-004: Session Cookie Missing `Secure`/`SameSite` Flags**

Description: The `connect.sid` cookie only sets `HttpOnly`; `Secure` and `SameSite` aren't explicitly configured.

Detailed Report: [BUG-SEC-004 Report](docs/bugs/BUG-SEC-004.md)

**BUG-SEC-005: Hardcoded Session Secret → Full Admin Impersonation (CRITICAL)**

Description: `config/session.js` uses the literal string `"super-secret"` as the session-signing secret instead of an environment variable. Proven via a working proof of concept: a session cookie forged from scratch (signed with that secret, without ever calling `/login`) is accepted by the server and grants full admin access.

Proof: `features/security/hardening.feature`, scenario "A session cookie forged with the hardcoded secret should not grant access" — inserts a session directly into MongoDB, signs the cookie with the same `cookie-signature` algorithm, and confirms `GET /admin/products` returns the full admin panel using only that cookie.

Detailed Report: [BUG-SEC-005 Report](docs/bugs/BUG-SEC-005.md)

## 10. Challenges and Key Decisions

**Migration from Cypress/Cucumber (JS) to Playwright/pytest-bdd (Python):** decision documented in detail in [ROADMAP.md](ROADMAP.md), including a step-by-step mapping of each Cypress pattern to its Playwright equivalent.

**External Payment Automation (Stripe) — full checkout:** the Cypress version needed `cy.origin()` just to validate the redirect to `checkout.stripe.com`, without being able to interact with the page itself (cross-origin/iframes were unstable). Playwright doesn't have this limitation — cross-origin navigation is native — and, in practice, the hosted Stripe page's card fields render directly in the main document (not in a cross-origin iframe), which made direct automation possible. The `purchase_flow.feature` scenario now completes the real flow: fills in the test card (`4242 4242 4242 4242`) using a real test key (`sk_test_...`), confirms payment, and validates the redirect through to `/orders/success`. Tested and reliable across all 3 matrix browsers (Chromium, Firefox, WebKit) — the hCaptcha present on the page didn't block automation on any of them.

**Reliability bug found in the application (outside the original security scope):** while validating the purchase flow locally, a failure creating the Stripe session (e.g. an invalid key) crashed the entire Node process (`unhandled promise rejection` with no handling), taking the application down for every user. Fixed directly in the `wde` repository (try/catch around the Stripe call).

**CI/CD with known bugs:** running `authorization.feature` (which documents real bugs) in the standard pipeline left the build permanently red, even when nothing was actually broken. The fix was marking the scenarios `@xfail` with `xfail_strict = true`, preserving coverage and the original intent (failing is the expected behavior) without masking real regressions.

**Code Structure:** kept the same philosophy as the Cypress version — unified Page Objects (`pages/`) and Step Definitions organized by feature (`steps/`), with shared steps (like role-parameterized login) centralized in `steps/conftest.py`.

**Visual regression — another Python vs. JS/TS gap in Playwright:** just like "UI mode" (`--ui`), `expect(page).to_have_screenshot()` only exists in the JS/TS test runner — confirmed via an exhaustive search of the installed Python API (`playwright/_impl/_assertions.py`, `playwright/sync_api/_generated.py`). The equivalent adopted was the third-party package `pytest-playwright-visual-snapshot`. Since it embeds the platform name in the snapshot filename, generating baselines on Windows would make them useless for CI (`ubuntu-latest`); the fix was generating them inside Playwright's own official Docker image, connected to the application's `docker-compose.yml` network (see section 7.9). This also exposed a Chromium side effect: the Compose service name `app` collides with the `.app` gTLD's HSTS preload, forcing HTTPS and breaking the plain HTTP connection — worked around by using the container name (`wde-app-1`) instead of the service name.

## 11. Next Steps (Suggestions)

See the "Phase 9" section of [ROADMAP.md](ROADMAP.md) for the full list of improvements enabled by the Playwright migration. All items are now complete: multi-browser matrix (Chromium/Firefox/WebKit) in CI, parallel execution via `pytest-xdist`, full Stripe test checkout, lightweight API coverage via `playwright.request` (used in the security tests), and visual regression (`features/visual/`, section 7.9).

See [ROADMAP.md](ROADMAP.md)'s "Phase 10" for the current initiative: converting this suite to English (this document included), a real EN/PT-BR language selector in the app itself, a catalog overhaul (departments, filter, sort, search), a further set of checklist-driven UI features, and email/OTP integration.
