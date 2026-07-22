import pytest
from playwright.sync_api import expect
from pytest_bdd import given, parsers


@pytest.fixture
def scenario_context():
    """Mutable dict for sharing state between steps within a single scenario, equivalent to Cypress aliases.

    Named to avoid colliding with pytest-playwright's own `context` fixture (the BrowserContext).
    """
    return {}


@given(parsers.parse('que eu estou logado como "{user_type}"'))
def logged_in_as(user_type, login_as, page):
    """Shared login step, equivalent to commonSteps.js, used via Background/Contexto."""
    login_as(user_type)

    if user_type.lower() == "cliente":
        expect(page.locator("#main-header").get_by_role("link", name="Orders")).to_be_visible()
