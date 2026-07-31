import pytest
from playwright.sync_api import expect
from pytest_bdd import given, parsers


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
