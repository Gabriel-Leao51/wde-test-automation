import os

import pymongo
from playwright.sync_api import expect
from pytest_bdd import parsers, scenarios, then, when

scenarios("catalog/catalog_filter_sort.feature")

MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = "online-shop"


@when(parsers.parse('I visit the product catalog filtered by department "{department}"'))
def visit_catalog_filtered_by_department(page, department):
    page.goto(f"/products?department={department}")


@when(parsers.parse('I visit the product catalog sorted by "{sort}"'))
def visit_catalog_sorted(page, sort):
    page.goto(f"/products?sort={sort}")


@then(parsers.parse('only products from the "{department}" department should be listed'))
def assert_only_department_products_listed(page, department):
    # Compare against the database directly (the source of truth for what belongs
    # to a department) rather than a second hardcoded list of titles in the test,
    # which would drift from the seed data over time.
    client = pymongo.MongoClient(MONGODB_URI)
    expected_titles = {doc["title"] for doc in client[DB_NAME].products.find({"department": department})}
    client.close()

    rendered_titles = set(page.locator("article.product-item h2").all_inner_texts())

    assert rendered_titles, "no products rendered - department filter may be broken"
    assert rendered_titles == expected_titles, (
        f"department filter mismatch for '{department}': "
        f"expected {expected_titles}, got {rendered_titles}"
    )


@then(parsers.parse("the listed products should be in {order} alphabetical order"))
def assert_alphabetical_order(page, order):
    titles = page.locator("article.product-item h2").all_inner_texts()
    expected = sorted(titles, reverse=(order == "descending"))
    assert titles == expected, f"titles not in {order} alphabetical order: {titles}"


@then(parsers.parse("the listed products should be in {order} price order"))
def assert_price_order(page, order):
    price_texts = page.locator("article.product-item .product-item-price").all_inner_texts()
    prices = [float(text.lstrip("$")) for text in price_texts]
    expected = sorted(prices, reverse=(order == "descending"))
    assert prices == expected, f"prices not in {order} order: {prices}"


@then("the product catalog page should load successfully")
def assert_catalog_page_loaded(page):
    expect(page.get_by_role("heading", name="All Products", level=1)).to_be_visible()
    expect(page.locator("article.product-item").first).to_be_visible()
