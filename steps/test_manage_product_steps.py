import re

from playwright.sync_api import expect
from pytest_bdd import given, parsers, scenarios, then, when

from utils.helpers import format_product_data

scenarios("admin/manage_product.feature")


# --- Contexto ---


@given(parsers.parse('eu estou na pagina inicial do painel administrativo "{expected_path}"'))
def assert_on_admin_home_page(page, expected_path):
    expect(page).to_have_url(re.compile(re.escape(expected_path)))


@when(parsers.parse('eu navego para a pagina de gerenciamento de produtos "{link_text}"'))
def navigate_to_manage_products(products_page, link_text):
    products_page.click_manage_products_link()


# --- Steps genéricos reutilizados entre cenários ---


@when(parsers.parse('eu clico no botao "{button_text}"'))
def click_generic_button(page, products_page, button_text):
    if button_text == "Add Product":
        products_page.click_add_new_product_button()
    elif button_text == "Save":
        products_page.click_save_button()
    else:
        locator = page.locator("button, .btn, a.btn").filter(has_text=button_text).first
        expect(locator).to_be_visible()
        locator.click()


@when(parsers.parse('eu clico no botao "{button_text}" para o produto de titulo "{product_title}"'))
def click_button_for_product(products_page, scenario_context, button_text, product_title):
    if button_text == "View & Edit":
        products_page.click_edit_product_button(product_title)
    elif button_text == "Delete":
        scenario_context["deleted_product_id"] = products_page.click_delete_product_button(product_title)
    else:
        raise ValueError(f'Ação para o botão "{button_text}" não implementada para produtos.')


@then(parsers.parse('eu devo ser redirecionado para a pagina de gerenciamento de produtos "{expected_path}"'))
def assert_redirected_to_manage_products(page, expected_path):
    expect(page).to_have_url(re.compile(re.escape(expected_path)))


# --- Steps: Adicionar Produto ---


@when("eu preencho o formulario de adicionar produto com os seguintes dados:")
def fill_add_product_form(products_page, datatable):
    product_data = format_product_data(datatable)
    products_page.fill_product_form(product_data)


@then(parsers.parse('o produto "{product_title}" deve estar visivel na listagem de produtos com titulo e imagem'))
def assert_product_added(products_page, product_title):
    products_page.assert_product_added_successfully(product_title)


# --- Steps: Editar Produto ---


@when("eu preencho o formulario de edição de produto com os seguintes dados:")
def fill_edit_product_form(products_page, datatable):
    product_data = format_product_data(datatable)
    products_page.fill_edit_product_form(product_data)


@then(parsers.parse('o produto "{product_title}" deve ser exibido na listagem de produtos com o titulo atualizado'))
def assert_product_edited(products_page, product_title):
    products_page.assert_product_edited_successfully(product_title)


# --- Steps: Excluir Produto ---


@then(parsers.parse('o produto "{product_title}" não deve ser mais exibido na listagem de produtos'))
def assert_product_deleted(products_page, scenario_context, product_title):
    products_page.assert_product_deleted_successfully(scenario_context["deleted_product_id"])


# --- Steps: Validação (Campo Obrigatório) ---


@then("eu devo ver uma mensagem de erro informando que os campos obrigatorios devem ser preenchidos")
def assert_required_field_error(products_page):
    validity = products_page.product_title_input.evaluate(
        "el => ({ valid: el.validity.valid, message: el.validationMessage })"
    )
    assert validity["valid"] is False
    assert validity["message"] == "Please fill out this field."


@then("eu devo permanecer na pagina de adicionar produto")
def assert_still_on_new_product_page(page):
    expect(page).to_have_url(re.compile(r".*/admin/products/new"))
