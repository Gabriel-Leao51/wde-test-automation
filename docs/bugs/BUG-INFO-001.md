# BUG-INFO-001: Exposure of Internal Server Details on Error Pages

## Severity

**HIGH**

- **Justification:** Any unhandled error (not just the scenario reproduced here) exposes full server filesystem paths, EJS template source-code snippets, and Node.js stack traces directly to the client — including unauthenticated users. This makes it easier for an attacker to fingerprint the stack and internal structure of the application when planning further attacks.

## Priority

**HIGH**

## Environment

- **Application:** WDE Shop
- **Base URL:** `http://localhost:3000` (local stack via Docker Compose, see `wde/docker-compose.yml`)
- **Affected Endpoint:** any route that triggers an unhandled exception and falls into `errorHandlerMiddleware` — reproduced here via `POST /cart/items` without a valid CSRF token
- **User Profile:** unauthenticated (no login required)

## Report Details

- **Reported by:** Gabriel Leão (with assistance from Claude)
- **Date discovered:** 2026-07-24
- **Context:** found while expanding the test suite's security coverage, investigating `csurf`'s behavior for requests without a valid CSRF token.

## Steps to Reproduce

1. While unauthenticated, send a `POST` request to a CSRF-protected endpoint (e.g. `/cart/items`) **without** including the `_csrf` parameter:
   ```bash
   curl -X POST http://localhost:3000/cart/items --data-urlencode "productId=<valid-id>"
   ```
2. Observe the HTTP response.

## Expected Result

- A generic error response (ideally `403 Forbidden` for an invalid/missing CSRF token), with no implementation details, file paths, or stack traces.

## Actual Result (Failure)

- The response is `500 Internal Server Error` containing the full HTML of Express's default error handler, including:
  - Absolute server paths (`/usr/src/app/views/shared/500.ejs`, `/usr/src/app/views/shared/includes/header.ejs`, etc.)
  - EJS template source-code snippets
  - A full stack trace, including `node_modules` paths

Real captured response excerpt:

```
TypeError: /usr/src/app/views/shared/500.ejs:4
    2| </head>
    3| <body>
 >> 4|   <%- include('includes/header') %>
...
Cannot read properties of undefined (reading 'totalQuantity')
    at eval ("/usr/src/app/views/shared/includes/nav-items.ejs":15:38)
    ...
```

## Evidence

- **Automated Test:** `features/security/hardening.feature`, scenario "Internal errors should not expose server file paths and source code" (`@xfail`, tag `@error-handling`) — intentionally fails against the current behavior, proving the exposure.
- **Manual reproduction:** the `curl` command above, tested on 2026-07-24 against the local stack.

## Root Cause Analysis

Two causes combine to produce this result:

1. **`NODE_ENV` is never set to `production`** anywhere (`Dockerfile`, `docker-compose.yml`, or the application code itself). Express defaults to development mode, which includes verbose error details in responses — correct behavior for local debugging, but never disabled before a "real" run of the stack.
2. **Cascading failure in the error handler itself:** `middlewares/error-handler.js` tries to render `views/shared/500.ejs`, which includes `header.ejs` → `nav-items.ejs`. That last template reads `locals.cart.totalQuantity` unconditionally. Since `csurf()` is registered in `app.js` **before** `cartMiddleware`, a CSRF rejection never reaches the point where `res.locals.cart` gets populated — rendering the error page itself throws a new exception, and Express falls back to its default error handler (which is what actually leaks the internal details).

Important: this specific chain of events **does not crash the Node process** (unlike the already-fixed NoSQL injection bug) — it's a synchronous failure during rendering, caught by Express itself. The problem is purely information exposure and a broken error UX, not availability.

## Potential Impact

- Leaks the server's and application's internal structure, useful for an attacker mapping the technology stack to plan more targeted attacks.
- Any other unhandled error elsewhere in the application is subject to the same leak, not just the CSRF path used to reproduce it here.
- End users see a genuinely broken error page (the application's own error page fails to render) instead of a friendly message.

## Recommendations

1. Set `NODE_ENV=production` in the stack's run configuration (`wde` repository's `docker-compose.yml`), ensuring Express never exposes error details in any environment other than explicit local development.
2. Fix `nav-items.ejs` to not assume `locals.cart` always exists (e.g. `locals.cart?.totalQuantity || 0`, or ensure a default value on `res.locals` before any possibility of an error).
3. Standardize `errorHandlerMiddleware` so a failure in rendering the error page itself never escapes to Express's default handler — for example, wrapping `res.render` in a try/catch with a plain-text fallback.
4. Ensure CSRF errors return a more precise status code (`403`) instead of the generic `500`.
