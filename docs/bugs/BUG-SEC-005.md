# BUG-SEC-005: Hardcoded Session Secret in Source Code

## Severity

**CRITICAL**

- **Justification:** Proven via an automated proof of concept (see Evidence): knowing the value `"super-secret"` is enough to forge a correctly-signed `connect.sid` cookie and gain full admin access (`/admin/products` renders successfully) **without ever calling `/login` and without knowing any credentials**. This isn't "potentially" exploitable — it's end-to-end admin impersonation, proven in this round.

## Priority

**HIGH**

- **Justification:** Not remotely exploitable by an attacker without access to the secret (which today only lives in the source code), but once the secret is obtained, the impact is total and immediate — no password, stolen session token, or any other credential needed. Real risk if the repository is (or becomes) public, or in the event of a source code leak.

## Environment

- **Application:** WDE Shop
- **File:** `config/session.js`

## Report Details

- **Reported by:** Gabriel Leão (with assistance from Claude)
- **Date discovered:** 2026-07-24

## Steps to Reproduce

1. Inspect `config/session.js` in the repository:

   ```js
   function createSessionConfig() {
     return {
       secret: "super-secret",
       resave: false,
       saveUninitialized: false,
       store: createSessionStore(),
       cookie: {
         maxAge: 2 * 24 * 60 * 60 * 1000,
       },
     };
   }
   ```

2. The value `"super-secret"` is the secret `express-session` uses (via `cookie-signature`) to sign the `connect.sid` cookie. Anyone with that value can generate a valid signature for an arbitrary `sessionID` and present it to the server as if it were a legitimate session.

3. **Full proof of concept** (reproduced in `steps/test_security_hardening_steps.py`, function `forge_admin_session_cookie` + scenario "A session cookie forged with the hardcoded secret should not grant access" in `features/security/hardening.feature`):

   a. Connect directly to MongoDB (`sessions` collection, same schema used by `connect-mongodb-session`) and insert an arbitrary session document, with `uid` pointing at a real admin user's `_id` and `isAdmin: true` — without ever having logged in:

      ```python
      db.sessions.insert_one({
          "_id": forged_sid,
          "session": {"cookie": {...}, "uid": str(admin_user["_id"]), "isAdmin": True},
          "expires": expires_at,
      })
      ```

   b. Sign the chosen `sid` with the same algorithm `cookie-signature` uses (`HMAC-SHA256` in base64, no padding), using the hardcoded secret:

      ```python
      mac = hmac.new(b"super-secret", forged_sid.encode(), hashlib.sha256).digest()
      cookie_value = f"s:{forged_sid}." + base64.b64encode(mac).decode().rstrip("=")
      ```

   c. Make a `GET /admin/products` request using **only** that forged cookie, in a brand-new, fully isolated request context (no cookies from any real session).

## Expected Result

The session secret should come from an environment variable (e.g. `process.env.SESSION_SECRET`), randomly generated and never committed to version control — following the same pattern already used for `MONGODB_URI` and `STRIPE_KEY` in this project. A cookie forged this way should not be accepted by the server.

## Actual Result (Failure)

- The secret is a fixed literal string in the source code, identical across every instance of the application and visible to anyone with access to the repository (including the entire commit history, even if it's changed in a future commit).
- **Confirmed by a real run:** the `GET /admin/products` request with the forged cookie returned `200 OK` with the full admin panel HTML (`Manage Products` present in the response) — admin access obtained without ever calling `/login`.

## Evidence

- **Source code:** `wde/config/session.js`, the `secret` field's line.
- **Automated Test (working proof of concept):** `features/security/hardening.feature`, scenario "A session cookie forged with the hardcoded secret should not grant access" (`@xfail`, tag `@session`) — forges a cookie from scratch (without depending on any pre-existing session) and proves the server grants admin access based on it alone.

## Root Cause Analysis

The value was likely left as a placeholder during initial development and never migrated to environment-based configuration, unlike the application's other secrets (`MONGODB_URI`, `STRIPE_KEY`), which have been read from environment variables ever since the project was dockerized.

## Potential Impact (Confirmed)

- **Full impersonation of any user, including administrators, without knowing any credentials** — demonstrated in this round via a working proof of concept, contingent only on the secret being exposed (e.g. the repository becoming public, a source code leak).
- Even if the secret is rotated in the future, the current value remains in the Git history indefinitely, unless the history is rewritten.

## Recommendations

1. Move `secret` to an environment variable (`SESSION_SECRET`), following the `.env`/`.env.example` pattern already established in the project.
2. Generate a strong random value (e.g. `openssl rand -base64 32`) for each environment.
3. Add instructions to `README.md` for setting `SESSION_SECRET` in `.env`.
