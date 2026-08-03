import os

import pymongo
from playwright.sync_api import expect
from pytest_bdd import parsers, scenarios, then, when

scenarios("catalog/catalog_filter_sort.feature")

MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = "online-shop"


# "Given I am on the product catalog" is defined in steps/conftest.py (shared
# across step files, same pattern as the "logged in as" step).


@when(parsers.parse('I visit the product catalog filtered by department "{department}"'))
def visit_catalog_filtered_by_department(page, department):
    page.goto(f"/products?department={department}")


@when(parsers.parse('I select "{option_label}" from the department filter'))
def select_department_filter(page, option_label):
    page.locator("#department-filter").select_option(label=option_label)


@when(parsers.parse('I select "{option_label}" from the sort dropdown'))
def select_sort_dropdown(page, option_label):
    page.locator("#sort-select").select_option(label=option_label)


@when(parsers.parse('I click the "{button_text}" button'))
def click_button(page, button_text):
    page.locator("button, .btn, a.btn").filter(has_text=button_text).first.click()


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

    # The preceding step (a "Filter" button click or a direct page.goto) triggers
    # a full navigation; all_inner_texts() takes a one-shot synchronous snapshot
    # with no auto-retry, so reading it before the new page has settled can hit
    # "Execution context was destroyed" mid-navigation (seen on WebKit's timing,
    # not Chromium/Firefox's). Wait for real content to be visible first.
    expect(page.locator("article.product-item").first).to_be_visible()
    rendered_titles = set(page.locator("article.product-item h2").all_inner_texts())

    assert rendered_titles, "no products rendered - department filter may be broken"
    assert rendered_titles == expected_titles, (
        f"department filter mismatch for '{department}': "
        f"expected {expected_titles}, got {rendered_titles}"
    )


@then(parsers.parse("the listed products should be in {order} alphabetical order"))
def assert_alphabetical_order(page, order):
    # See the comment in assert_only_department_products_listed - same
    # post-navigation race with all_inner_texts() being a one-shot read.
    expect(page.locator("article.product-item").first).to_be_visible()
    titles = page.locator("article.product-item h2").all_inner_texts()
    expected = sorted(titles, reverse=(order == "descending"))
    assert titles == expected, f"titles not in {order} alphabetical order: {titles}"


@then(parsers.parse("the listed products should be in {order} price order"))
def assert_price_order(page, order):
    expect(page.locator("article.product-item").first).to_be_visible()
    price_texts = page.locator("article.product-item .product-item-price").all_inner_texts()
    prices = [float(text.lstrip("$")) for text in price_texts]
    expected = sorted(prices, reverse=(order == "descending"))
    assert prices == expected, f"prices not in {order} order: {prices}"


@then("the product catalog page should load successfully")
def assert_catalog_page_loaded(page):
    expect(page.get_by_role("heading", name="All Products", level=1)).to_be_visible()
    expect(page.locator("article.product-item").first).to_be_visible()


# --- Live search (combobox) ---


@when(parsers.parse('I type "{query}" into the product search box'))
def type_into_search_box(page, query):
    page.locator("#product-search").fill(query)


@then(parsers.parse('I should see search suggestions including "{title}"'))
def assert_search_suggestion_visible(page, title):
    expect(page.locator("#product-search-results").get_by_role("option").filter(has_text=title)).to_be_visible()


@when(parsers.parse('I click the search suggestion "{title}"'))
def click_search_suggestion(page, title):
    page.locator("#product-search-results").get_by_role("option").filter(has_text=title).click()


@when(parsers.parse('I request the search API with query "{query}"'))
def request_search_api(playwright, base_url, scenario_context, query):
    # Same isolated playwright.request pattern used for the BUG-SEC-005 PoC -
    # a raw HTTP call, no browser needed, exercising the JSON contract directly.
    request_context = playwright.request.new_context(base_url=base_url)
    scenario_context["search_response"] = request_context.get(f"/api/products/search?q={query}")
    scenario_context["search_request_context"] = request_context


@then(parsers.parse('the JSON response should include a product titled "{title}"'))
def assert_json_response_includes_title(scenario_context, title):
    body = scenario_context["search_response"].json()
    scenario_context["search_request_context"].dispose()

    titles = [item["title"] for item in body["results"]]
    assert title in titles, f"expected '{title}' in search results: {titles}"
