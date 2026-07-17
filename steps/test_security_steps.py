import re

from playwright.sync_api import expect
from pytest_bdd import parsers, scenarios, then, when

scenarios("admin/authentication.feature")
scenarios("admin/authorization.feature")


# --- authentication.feature (visitante não autenticado) ---


@when(parsers.parse('eu tento acessar a URL "{path}" sem estar logado'))
def visit_url_unauthenticated(page, path):
    page.context.clear_cookies()
    page.goto(path)


@then("eu devo ser direcionado para a página de erro 401")
def assert_redirected_to_401(page):
    expect(page).to_have_url(re.compile(r".*/401"))


@then("eu devo ver os elementos da página de não autenticado")
def assert_unauthenticated_page_elements(page):
    expect(page.get_by_role("heading", name="Not authenticated!", level=1)).to_be_visible()
    expect(page.get_by_text("You are not authenticated!")).to_be_visible()
    expect(
        page.get_by_role("link", name=re.compile("back to safety!", re.IGNORECASE))
    ).to_be_visible()


# --- authorization.feature (cliente logado, sem permissão de admin) ---


@when(parsers.parse('eu tento acessar a URL "{path}"'))
def visit_url(page, path):
    page.goto(path)


@then("eu NÃO devo conseguir acessar a página de Produtos do Admin")
def assert_admin_products_page_not_accessible(page):
    expect(page.locator('a[href*="/admin/products/new"]')).to_have_count(0)
    expect(
        page.get_by_role("heading", name=re.compile("manage products", re.IGNORECASE), level=2)
    ).to_have_count(0)


@then("eu devo ver uma mensagem indicando falta de autorização")
def assert_authorization_message_visible(page):
    expect(
        page.get_by_text(
            re.compile("not authorized - you are not authorized to access this page!", re.IGNORECASE)
        )
    ).to_be_visible()
    expect(page).not_to_have_url(re.compile(r"/admin/(products|orders)/\d+"))
    expect(page).not_to_have_url(re.compile(r"/admin/(products|orders)/new"))


@then("eu NÃO devo conseguir acessar o formulário de Edição de Produto")
def assert_edit_product_form_not_accessible(page):
    expect(page.get_by_role("button", name=re.compile("save", re.IGNORECASE))).to_have_count(0)
