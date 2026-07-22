import re

from playwright.sync_api import expect
from pytest_bdd import given, parsers, scenarios, then, when

scenarios("admin/login.feature")


# --- Cenário: Login administrativo bem-sucedido ---


@given("que eu estou na pagina de login administrativo")
def visit_admin_login_page(login_page):
    login_page.visit()


@when("eu insiro um email de administrador valido")
def type_valid_admin_email(login_page, users):
    login_page.type_email(users["admin"]["email"])


@when("eu insiro uma senha de administrador valida")
def type_valid_admin_password(login_page, users):
    login_page.type_password(users["admin"]["password"])


@when(parsers.parse('eu clico no botao de "{button_text}"'))
def click_login_button(login_page, button_text):
    login_page.click_login_button()


@then("eu devo ser redirecionado para a pagina principal do painel administrativo")
def assert_redirected_to_admin_home(page):
    expect(page).to_have_url(re.compile(r".*/products"))


@then(parsers.parse('eu devo ver as opcoes de menu "{manage_products}" e "{manage_orders}"'))
def assert_menu_options_visible(page, manage_products, manage_orders):
    header = page.locator("#main-header")
    expect(header.get_by_role("link", name=manage_products)).to_be_visible()
    expect(header.get_by_role("link", name=manage_orders)).to_be_visible()


@then(parsers.parse('eu devo ver o botao "{logout_text}" no cabecalho'))
def assert_logout_button_visible(page, logout_text):
    expect(page.locator("#main-header").get_by_role("button", name=logout_text)).to_be_visible()


# --- Cenário: Login administrativo falha - Credenciais invalidas ---


@given("que eu estou na pagina de login")
def visit_login_page(login_page):
    login_page.visit()


@when("eu insiro um email invalido")
def type_invalid_email(login_page, users):
    login_page.type_email(users["invalidAdmin"]["email"])


@when("eu insiro uma senha invalida")
def type_invalid_password(login_page, users):
    login_page.type_password(users["invalidAdmin"]["password"])


@when(parsers.parse('eu clico no botão de "{button_text}"'))
def click_login_button_accented(login_page, button_text):
    login_page.click_login_button()


@then("eu devo ver uma mensagem de erro")
def assert_error_message_visible(login_page):
    login_page.check_error_message()


@then("eu devo permanecer na pagina de login")
def assert_still_on_login_page(page):
    expect(page).to_have_url(re.compile(r".*/login"))
