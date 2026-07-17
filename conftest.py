import json
import os
from pathlib import Path

import pytest

from pages.cart_page import CartPage
from pages.login_page import LoginPage
from pages.orders_page import OrdersPage
from pages.products_page import ProductsPage

TEST_DATA_DIR = Path(__file__).resolve().parent / "test_data"


@pytest.fixture(scope="session")
def base_url():
    """Overrides pytest-playwright's base_url fixture.

    Defaults to the local Docker stack (see ../wde/docker-compose.yml).
    Set WDE_BASE_URL to point at a different environment (e.g. in CI).
    """
    return os.environ.get("WDE_BASE_URL", "http://localhost:3000")


@pytest.fixture(scope="session")
def users():
    with open(TEST_DATA_DIR / "users.json", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def login_page(page):
    return LoginPage(page)


@pytest.fixture
def products_page(page):
    return ProductsPage(page)


@pytest.fixture
def cart_page(page):
    return CartPage(page)


@pytest.fixture
def orders_page(page):
    return OrdersPage(page)


@pytest.fixture
def login_as(login_page, users):
    """Factory fixture equivalent to commonSteps.js's 'que eu estou logado como {string}'."""

    def _login_as(role: str):
        role_key = role.lower()
        credentials = users.get(role_key)

        if not credentials or not credentials.get("email") or not credentials.get("password"):
            raise ValueError(f'Credenciais para "{role_key}" não encontradas em users.json')

        login_page.login(credentials["email"], credentials["password"])
        return credentials

    return _login_as
