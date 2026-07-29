import re

from playwright.sync_api import expect
from pytest_bdd import given, parsers, scenarios, then, when

scenarios("admin/login.feature")


# --- Scenario: Successful admin login ---


@given("I am on the admin login page")
def visit_admin_login_page(login_page):
    login_page.visit()


@when("I enter a valid admin email")
def type_valid_admin_email(login_page, users):
    login_page.type_email(users["admin"]["email"])


@when("I enter a valid admin password")
def type_valid_admin_password(login_page, users):
    login_page.type_password(users["admin"]["password"])


@when(parsers.parse('I click the "{button_text}" button'))
def click_login_button(login_page, button_text):
    login_page.click_login_button()


@then("I should be redirected to the admin panel home page")
def assert_redirected_to_admin_home(page):
    expect(page).to_have_url(re.compile(r".*/products"))


@then(parsers.parse('I should see the "{manage_products}" and "{manage_orders}" menu options'))
def assert_menu_options_visible(page, manage_products, manage_orders):
    header = page.locator("#main-header")
    expect(header.get_by_role("link", name=manage_products)).to_be_visible()
    expect(header.get_by_role("link", name=manage_orders)).to_be_visible()


@then(parsers.parse('I should see the "{logout_text}" button in the header'))
def assert_logout_button_visible(page, logout_text):
    expect(page.locator("#main-header").get_by_role("button", name=logout_text)).to_be_visible()


# --- Scenario: Admin login fails - Invalid credentials ---


@given("I am on the login page")
def visit_login_page(login_page):
    login_page.visit()


@when("I enter an invalid email")
def type_invalid_email(login_page, users):
    login_page.type_email(users["invalidAdmin"]["email"])


@when("I enter an invalid password")
def type_invalid_password(login_page, users):
    login_page.type_password(users["invalidAdmin"]["password"])


@then("I should see an error message")
def assert_error_message_visible(login_page):
    login_page.check_error_message()


@then("I should remain on the login page")
def assert_still_on_login_page(page):
    expect(page).to_have_url(re.compile(r".*/login"))
