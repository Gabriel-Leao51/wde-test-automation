import re

from playwright.sync_api import expect
from pytest_bdd import parsers, scenarios, then, when

scenarios("client/purchase_flow.feature")


@when(parsers.parse('eu clico em "View Details" para o produto "{product_title}"'))
def click_view_details(products_page, product_title):
    products_page.click_view_details_button(product_title)


@when('eu clico no botão "Add to Cart" na página de detalhes do produto')
def click_add_to_cart(products_page):
    products_page.click_add_to_cart_button()


@then(parsers.parse('o indicador do carrinho na barra de navegação deve ser atualizado para "{expected_count}"'))
def assert_cart_indicator(page, expected_count):
    badge = page.locator("#main-header").locator(".nav-items a", has_text="Cart").locator("span.badge")
    expect(badge).to_have_text(expected_count)


@when(parsers.parse('eu clico no link "{link_text}" da barra de navegação'))
def click_nav_link(page, link_text):
    page.locator("#main-header .nav-items a").filter(has_text=link_text).first.click()


@then(parsers.parse('eu devo ver o produto "{product_title}" listado no carrinho'))
def assert_product_in_cart(cart_page, product_title):
    cart_page.verify_product_in_cart(product_title)


@when('eu clico no botão "Buy Products"')
def click_buy_products(cart_page):
    cart_page.click_buy_products_button()


@then("eu devo ser redirecionado para a página de pagamento externa do Stripe")
def assert_redirected_to_stripe(page):
    expect(page).to_have_url(re.compile(r"checkout\.stripe\.com"), timeout=20000)
