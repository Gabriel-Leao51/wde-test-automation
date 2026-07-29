import json
from pathlib import Path

from pytest_bdd import given, parsers, scenarios, then, when

TEST_DATA_DIR = Path(__file__).resolve().parent.parent / "test_data"

scenarios("admin/manage_orders.feature")


# --- Background ---


@given("I navigate to the manage orders page")
def navigate_to_manage_orders(orders_page):
    orders_page.navigate_to_orders_page()


# --- Scenario ---


@given(parsers.parse('a known order with status "{status}" exists'))
def known_order_exists(scenario_context, status):
    with open(TEST_DATA_DIR / "orders.json", encoding="utf-8") as f:
        data = json.load(f)

    order_id = data.get("orderData", {}).get("testOrderId")
    if not order_id:
        raise ValueError(
            'Invalid "orders.json" fixture format or "testOrderId" not found. '
            'Expected: { "orderData": { "testOrderId": "..." } }'
        )

    scenario_context["order_id"] = order_id


@when("I locate the known order in the order list")
def locate_known_order(orders_page, scenario_context):
    orders_page.find_and_focus_order_container(scenario_context["order_id"])


@when(parsers.parse('I select the new status "{status}" for this order'))
def select_new_status(orders_page, status):
    orders_page.select_new_status_for_current_order(status)


@when(parsers.parse('I click the "{button_text}" button for this order'))
def click_update_for_order(orders_page, button_text):
    if button_text.lower() != "update":
        raise ValueError(f'Action for the "{button_text}" button is not implemented for orders.')
    orders_page.click_update_for_current_order()


@then(parsers.parse('the status "{expected_status}" should be displayed for this order'))
def assert_order_status(orders_page, expected_status):
    orders_page.assert_order_status_for_current_order(expected_status)
