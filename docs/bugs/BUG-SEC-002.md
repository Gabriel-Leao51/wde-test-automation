# BUG-SEC-002: Missing HTTP Security Headers

## Severity

**MEDIUM**

- **Justification:** None of the standard security headers are present in HTTP responses. Each absence is moderate risk on its own, but together they leave the application without defense-in-depth against clickjacking, MIME-sniffing, and reduce the effectiveness of other mitigations (like CSP against XSS). The `X-Powered-By: Express` header also makes fingerprinting the technology stack easier.

## Priority

**MEDIUM**

## Environment

- **Application:** WDE Shop
- **Base URL:** `http://localhost:3000`
- **Affected Endpoint:** all routes (tested on `/products`, but the behavior comes from the global Express configuration)

## Report Details

- **Reported by:** Gabriel Leão (with assistance from Claude)
- **Date discovered:** 2026-07-24

## Steps to Reproduce

```bash
curl -I http://localhost:3000/products
```

## Expected Result

Presence of standard security headers, for example:

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY` (or `SAMEORIGIN`)
- `Content-Security-Policy: ...`
- `Referrer-Policy: ...`
- Absence of the `X-Powered-By` header

## Actual Result (Failure)

Real captured response:

```
HTTP/1.1 200 OK
X-Powered-By: Express
Content-Type: text/html; charset=utf-8
Content-Length: 3164
ETag: W/"c5c-XiJXTqKGgMSMNLHHjVu1+4Q2hEE"
Set-Cookie: connect.sid=...; Path=/; Expires=...; HttpOnly
Date: ...
Connection: keep-alive
Keep-Alive: timeout=5
```

No security header is present, and `X-Powered-By: Express` reveals the technology stack.

## Evidence

- **Automated Test:** `features/security/hardening.feature`, scenario "The application should respond with standard security headers" (`@xfail`, tag `@headers`).
- **Manual reproduction:** the `curl -I` command above.

## Root Cause Analysis

No security middleware (e.g. [`helmet`](https://helmetjs.github.io/)) is registered in `app.js`. There's no manual security-header configuration anywhere in the application.

## Potential Impact

- Without `X-Frame-Options`/`frame-ancestors` (CSP), the application can be embedded in an `<iframe>` on a malicious site (clickjacking).
- Without `X-Content-Type-Options: nosniff`, browsers may try to guess the content type of responses, opening the door to MIME-sniffing attacks.
- Without CSP, there's no additional defense layer if an XSS vector is found in the future.
- `X-Powered-By: Express` makes it easy for an attacker to quickly identify the stack and look for framework/version-specific known vulnerabilities.

## Recommendations

1. Add [`helmet`](https://www.npmjs.com/package/helmet) as a dependency and register it early in the middleware chain in `app.js` — covers most of these items (including disabling `X-Powered-By`) with minimal configuration.
2. Configure a `Content-Security-Policy` appropriate for the inline scripts/styles already present in the application (`helmet` allows per-directive customization).
3. Review whether `frame-ancestors`/`X-Frame-Options` should be `DENY` (no legitimate iframe use case identified in the application).
