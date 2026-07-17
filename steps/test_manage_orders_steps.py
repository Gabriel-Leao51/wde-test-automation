import json
from pathlib import Path

from pytest_bdd import given, parsers, scenarios, then, when

TEST_DATA_DIR = Path(__file__).resolve().parent.parent / "test_data"

scenarios("admin/manage_orders.feature")


# --- Contexto ---


@given("eu navego para a pagina de gerenciamento de pedidos")
def navigate_to_manage_orders(orders_page):
    orders_page.navigate_to_orders_page()


# --- Cenário ---


@given(parsers.parse('que um pedido com status "{status}" conhecido existe'))
def known_order_exists(scenario_context, status):
    with open(TEST_DATA_DIR / "orders.json", encoding="utf-8") as f:
        data = json.load(f)

    order_id = data.get("orderData", {}).get("testOrderId")
    if not order_id:
        raise ValueError(
            'Fixture "orders.json" com formato inválido ou "testOrderId" não encontrado. '
            'Esperado: { "orderData": { "testOrderId": "..." } }'
        )

    scenario_context["order_id"] = order_id


@when("eu localizo o pedido conhecido na lista de pedidos")
def locate_known_order(orders_page, scenario_context):
    orders_page.find_and_focus_order_container(scenario_context["order_id"])


@when(parsers.parse('eu seleciono o novo status "{status}" para este pedido'))
def select_new_status(orders_page, status):
    orders_page.select_new_status_for_current_order(status)


@when(parsers.parse('eu clico no botao "{button_text}" deste pedido'))
def click_update_for_order(orders_page, button_text):
    if button_text.lower() != "update":
        raise ValueError(f'Ação para o botão "{button_text}" não implementada para pedidos.')
    orders_page.click_update_for_current_order()


@then(parsers.parse('o status "{expected_status}" deve ser exibido para este pedido'))
def assert_order_status(orders_page, expected_status):
    orders_page.assert_order_status_for_current_order(expected_status)
