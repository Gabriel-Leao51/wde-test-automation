# BUG-SEC-004: Session Cookie Missing `Secure`/`SameSite` Flags

## Severity

**MEDIUM**

- **Justification:** The session cookie (`connect.sid`) already has `HttpOnly` (protects against theft via XSS), but doesn't explicitly set `Secure` or `SameSite`. Without `Secure`, the cookie could be transmitted in plain text if the application is ever also served over plain HTTP alongside HTTPS. Without an explicit `SameSite`, the application relies on the client browser's default behavior instead of enforcing the policy itself, which is inconsistent across browsers/versions.

## Priority

**MEDIUM**

## Environment

- **Application:** WDE Shop
- **Base URL:** `http://localhost:3000`
- **Affected Endpoint:** any response that sets the session cookie (e.g. `GET /login`)

## Report Details

- **Reported by:** Gabriel Leão (with assistance from Claude)
- **Date discovered:** 2026-07-24

## Steps to Reproduce

```bash
curl -I http://localhost:3000/login
```

## Expected Result

The `Set-Cookie` header should include the `Secure` and `SameSite=Strict` (or `Lax`, depending on cross-site navigation needs) flags in addition to `HttpOnly`.

## Actual Result (Failure)

Real captured response:

```
Set-Cookie: connect.sid=s%3A...; Path=/; Expires=...; HttpOnly
```

Only `HttpOnly` is present. `Secure` and `SameSite` are absent.

## Evidence

- **Automated Test:** `features/security/hardening.feature`, scenario "The session cookie should have the Secure and SameSite flags configured" (`@xfail`, tag `@session`).
- **Manual reproduction:** the `curl -I` command above.

## Root Cause Analysis

`config/session.js` only configures the cookie's `maxAge`:

```js
cookie: {
  maxAge: 2 * 24 * 60 * 60 * 1000,
},
```

No `secure` or `sameSite` option is passed to `express-session`.

## Potential Impact

- Without `Secure`, the session cookie can travel unencrypted if the application is ever also exposed over HTTP in some environment.
- Without an explicit `SameSite`, the CSRF protection the browser would natively provide for cross-site requests is left to default behavior (varies by browser/version) instead of being guaranteed by the application.

## Recommendations

1. In `config/session.js`, explicitly set `cookie: { maxAge: ..., secure: true, sameSite: 'lax' }` (or `'strict'`, evaluating whether any legitimate flow depends on cross-site navigation — e.g. the return from Stripe Checkout).
2. Since the app only runs behind HTTPS in production, consider making `secure` conditional on the environment (`process.env.NODE_ENV === 'production'`) so local HTTP development doesn't break — but this should come together with the `BUG-INFO-001` fix (setting `NODE_ENV` correctly).
