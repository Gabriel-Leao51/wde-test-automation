import base64
import hashlib
import hmac
import os
import re
import uuid
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

import pymongo
from pytest_bdd import parsers, scenarios, then, when

scenarios("security/hardening.feature")

# Matches the literal value hardcoded in wde/config/session.js (BUG-SEC-005).
# A real attacker would learn this by reading the source, not by any request
# this suite makes - it's a source-level finding, exploited here to prove impact.
HARDCODED_SESSION_SECRET = "super-secret"
MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
SESSION_DB_NAME = "online-shop"


def _get_csrf_token(page, path="/login"):
    response = page.request.get(path)
    match = re.search(r'name="_csrf" value="([^"]*)"', response.text())
    return match.group(1)


# --- NoSQL injection (regression tests - the underlying bug is fixed) ---


@when(parsers.parse('eu envio um payload de NoSQL injection para "{path}"'))
def send_nosql_injection_payload(page, scenario_context, path):
    csrf_token = _get_csrf_token(page, path)
    payload = {"email": {"$ne": None}, "password": {"$ne": None}}
    if path == "/signup":
        payload.update(
            {
                "confirm-email": {"$ne": None},
                "fullname": "x",
                "street": "x",
                "postal": "x",
                "city": "x",
            }
        )
    scenario_context["response"] = page.request.post(f"{path}?_csrf={csrf_token}", data=payload)


@then("eu devo receber uma resposta de credenciais invalidas")
def assert_invalid_credentials_response(scenario_context):
    assert "Invalid credentials" in scenario_context["response"].text()


@then("a aplicacao deve permanecer no ar")
def assert_app_still_up(page):
    response = page.request.get("/products")
    assert response.status == 200


# --- Security headers ---


@when(parsers.parse('eu faco uma requisicao GET para "{path}"'))
def make_get_request(page, scenario_context, path):
    scenario_context["response"] = page.request.get(path)


@then(parsers.parse('a resposta deve conter o header "{header_name}" com valor "{header_value}"'))
def assert_header_value(scenario_context, header_name, header_value):
    headers = scenario_context["response"].headers
    assert headers.get(header_name) == header_value, f"headers: {headers}"


@then(parsers.parse('a resposta deve conter o header "{header_name}"'))
def assert_header_present(scenario_context, header_name):
    headers = scenario_context["response"].headers
    assert header_name in headers, f"headers: {headers}"


@then(parsers.parse('a resposta nao deve conter o header "{header_name}"'))
def assert_header_absent(scenario_context, header_name):
    headers = scenario_context["response"].headers
    assert header_name not in headers, f"headers: {headers}"


# --- CSRF token exposure in URL ---


@when("eu visito a pagina de novo produto")
def visit_new_product_page(page):
    page.goto("/admin/products/new")


@then("o atributo action do formulario nao deve conter \"_csrf\"")
def assert_csrf_not_in_form_action(page):
    form_action = page.locator("main form").first.get_attribute("action")
    assert "_csrf" not in (form_action or ""), f"form action: {form_action}"


# --- Session cookie flags ---


@then("o cookie de sessao deve ter a flag Secure habilitada")
def assert_session_cookie_secure(page):
    cookies = page.context.cookies()
    session_cookie = next(c for c in cookies if c["name"] == "connect.sid")
    assert session_cookie["secure"] is True, f"cookie: {session_cookie}"


@then("o cookie de sessao deve ter a flag SameSite configurada")
def assert_session_cookie_samesite(page):
    cookies = page.context.cookies()
    session_cookie = next(c for c in cookies if c["name"] == "connect.sid")
    assert session_cookie.get("sameSite") in ("Strict", "Lax"), f"cookie: {session_cookie}"


# --- Verbose error / information disclosure ---


@when("eu envio uma requisicao que causa um erro interno no servidor")
def trigger_internal_server_error(page, scenario_context):
    # POST to a CSRF-protected endpoint without a token: csurf's own middleware rejects it
    # before cartMiddleware ever runs, so the error page's nav render crashes too (BUG-INFO-001).
    scenario_context["response"] = page.request.post(
        "/cart/items", data={"productId": "000000000000000000000001"}
    )


@then("a resposta nao deve conter caminhos do sistema de arquivos do servidor")
def assert_no_filesystem_paths_leaked(scenario_context):
    body = scenario_context["response"].text()
    assert "/usr/src/app" not in body, "response body leaks server filesystem paths"


@then("a resposta nao deve conter trechos de codigo-fonte do servidor")
def assert_no_source_code_leaked(scenario_context):
    body = scenario_context["response"].text()
    assert "node_modules" not in body, "response body leaks server source/stack trace details"


# --- Session cookie forgery via the hardcoded secret (BUG-SEC-005) ---


def _sign_session_id(sid: str, secret: str) -> str:
    """Replicates the `cookie-signature` npm package's sign() algorithm exactly
    (see wde's node_modules/cookie-signature/index.js): `<sid>.<base64-hmac-sha256>`,
    prefixed with express-session's "s:" marker.
    """
    mac = hmac.new(secret.encode(), sid.encode(), hashlib.sha256).digest()
    signature = base64.b64encode(mac).decode().rstrip("=")
    return f"s:{sid}.{signature}"


@when("eu forjo um cookie de sessao de administrador usando o segredo hardcoded do codigo-fonte")
def forge_admin_session_cookie(scenario_context):
    client = pymongo.MongoClient(MONGODB_URI)
    db = client[SESSION_DB_NAME]

    admin_user = db.users.find_one({"email": "admin@test.com"})
    assert admin_user, "seeded admin user not found - is the WDE stack up and seeded?"

    # Matches the document shape connect-mongodb-session writes/reads
    # (idField "_id", data nested under "session", TTL under "expires").
    forged_sid = f"forged-{uuid.uuid4()}"
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

    db.sessions.insert_one(
        {
            "_id": forged_sid,
            "session": {
                "cookie": {
                    "originalMaxAge": 3600000,
                    "expires": expires_at.isoformat(),
                    "httpOnly": True,
                    "path": "/",
                },
                "uid": str(admin_user["_id"]),
                "isAdmin": True,
            },
            "expires": expires_at,
        }
    )
    client.close()

    signed_value = _sign_session_id(forged_sid, HARDCODED_SESSION_SECRET)
    scenario_context["forged_sid"] = forged_sid
    scenario_context["forged_cookie"] = quote(signed_value, safe="")


@when(parsers.parse('eu acesso "{path}" usando apenas o cookie forjado'))
def access_with_forged_cookie(playwright, base_url, scenario_context, path):
    # A brand-new, isolated request context - no ambient cookies from any
    # other step - so the only thing granting access (if anything does) is
    # the forged cookie itself.
    request_context = playwright.request.new_context(
        base_url=base_url,
        extra_http_headers={"Cookie": f"connect.sid={scenario_context['forged_cookie']}"},
    )
    scenario_context["forged_response"] = request_context.get(path)
    scenario_context["forged_request_context"] = request_context


@then("o acesso NAO deve ser concedido sem um login de verdade")
def assert_forged_session_does_not_grant_access(scenario_context):
    response = scenario_context["forged_response"]
    body = response.text()
    scenario_context["forged_request_context"].dispose()

    # Clean up the forged session regardless of the assertion outcome below.
    client = pymongo.MongoClient(MONGODB_URI)
    client[SESSION_DB_NAME].sessions.delete_one({"_id": scenario_context["forged_sid"]})
    client.close()

    assert "Manage Products" not in body, (
        "forged session cookie (signed with the hardcoded secret) granted admin "
        "access to /admin/products without ever logging in"
    )
