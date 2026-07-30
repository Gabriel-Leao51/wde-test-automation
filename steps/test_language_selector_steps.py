from playwright.sync_api import expect
from pytest_bdd import given, parsers, scenarios, then, when

scenarios("localization/language_selector.feature")


@given("I am on the product catalog")
def visit_product_catalog(page):
    page.goto("/products")


@given(parsers.parse('the language is set to "{lang}"'))
def set_language_given(set_language, lang):
    set_language(lang)


@when(parsers.parse('I click the "{language_code}" language link'))
def click_language_link(page, language_code):
    page.locator("#main-header").get_by_role("link", name=language_code, exact=True).click()


@then(parsers.parse('the navigation should show "{shop_label}" as the shop link'))
def assert_shop_link_label(page, shop_label):
    expect(page.locator("#main-header").get_by_role("link", name=shop_label, exact=True)).to_be_visible()


@then(parsers.parse('the product catalog heading should read "{catalog_heading}"'))
def assert_catalog_heading(page, catalog_heading):
    expect(page.get_by_role("heading", name=catalog_heading, level=1)).to_be_visible()


@when(parsers.parse('I view the product with id "{product_id}"'))
def view_product_with_id(page, product_id):
    page.goto(f"/products/{product_id}")


@then(parsers.parse('I should see the product titled "{title}"'))
def assert_product_title(page, title):
    expect(page.get_by_role("heading", name=title, level=1)).to_be_visible()
