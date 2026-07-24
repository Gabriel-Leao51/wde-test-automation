import re

from pytest_bdd import parsers, scenarios, then, when

scenarios("security/hardening.feature")


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
