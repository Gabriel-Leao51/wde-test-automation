import re

from playwright.sync_api import expect
from pytest_bdd import parsers, scenarios, then, when

scenarios("admin/authentication.feature")
scenarios("admin/authorization.feature")


# --- authentication.feature (unauthenticated visitor) ---


@when(parsers.parse('I try to access the URL "{path}" without being logged in'))
def visit_url_unauthenticated(page, path):
    page.context.clear_cookies()
    page.goto(path)


@then("I should be redirected to the 401 error page")
def assert_redirected_to_401(page):
    expect(page).to_have_url(re.compile(r".*/401"))


@then("I should see the unauthenticated page elements")
def assert_unauthenticated_page_elements(page):
    expect(page.get_by_role("heading", name="Not authenticated!", level=1)).to_be_visible()
    expect(page.get_by_text("You are not authenticated!")).to_be_visible()
    expect(
        page.get_by_role("link", name=re.compile("back to safety!", re.IGNORECASE))
    ).to_be_visible()


# --- authorization.feature (logged-in customer, no admin permission) ---


@when(parsers.parse('I try to access the URL "{path}"'))
def visit_url(page, path):
    page.goto(path)


@then("I should NOT be able to access the Admin Products page")
def assert_admin_products_page_not_accessible(page):
    expect(page.locator('a[href*="/admin/products/new"]')).to_have_count(0)
    expect(
        page.get_by_role("heading", name=re.compile("manage products", re.IGNORECASE), level=2)
    ).to_have_count(0)


@then("I should see a message indicating lack of authorization")
def assert_authorization_message_visible(page):
    expect(
        page.get_by_text(
            re.compile("not authorized - you are not authorized to access this page!", re.IGNORECASE)
        )
    ).to_be_visible()
    expect(page).not_to_have_url(re.compile(r"/admin/(products|orders)/\d+"))
    expect(page).not_to_have_url(re.compile(r"/admin/(products|orders)/new"))


@then("I should NOT be able to access the Edit Product form")
def assert_edit_product_form_not_accessible(page):
    expect(page.get_by_role("button", name=re.compile("save", re.IGNORECASE))).to_have_count(0)
