import pytest
from playwright.sync_api import expect
from pytest_bdd import given, parsers, then


@pytest.fixture
def scenario_context():
    """Mutable dict for sharing state between steps within a single scenario, equivalent to Cypress aliases.

    Named to avoid colliding with pytest-playwright's own `context` fixture (the BrowserContext).
    """
    return {}


@given(parsers.parse('I am logged in as "{user_type}"'))
def logged_in_as(user_type, login_as, page):
    """Shared login step, equivalent to commonSteps.js, used via Background."""
    login_as(user_type)

    if user_type.lower() == "customer":
        expect(page.locator("#main-header").get_by_role("link", name="Orders")).to_be_visible()


@given("I am on the product catalog")
def visit_product_catalog(page):
    page.goto("/products")


@then(parsers.parse('I should see the product titled "{title}"'))
def assert_product_title(page, title):
    expect(page.get_by_role("heading", name=title, level=1)).to_be_visible()


@then(parsers.parse('I should see a success toast saying "{message}"'))
def assert_success_toast(page, message):
    expect(page.locator(".toast-success").filter(has_text=message)).to_be_visible()


@then("the toast should disappear on its own")
def assert_toast_disappears(page):
    # Auto-dismiss is ~4s + a short fade; give it real headroom rather than
    # guessing the exact timing - this is what a dynamic wait means here.
    expect(page.locator(".toast")).to_have_count(0, timeout=6000)
