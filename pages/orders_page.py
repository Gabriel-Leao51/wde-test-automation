import re

from playwright.sync_api import Locator, Page, expect


class OrdersPage:
    def __init__(self, page: Page):
        self.page = page
        self.header = page.locator("#main-header")
        self.orders_menu_link = self.header.get_by_role("link", name="Manage Orders")
        self.current_order: Locator | None = None

    # --- Elementos (parametrizados) ---

    def _order_container(self, order_id: str):
        hidden_input = self.page.locator(
            f'input[type="hidden"][name="orderid"][value="{order_id}"]'
        )
        return self.page.locator("article.order-item").filter(has=hidden_input)

    @staticmethod
    def _status_select(order_container: Locator):
        return order_container.locator('select[name="status"]')

    @staticmethod
    def _update_button(order_container: Locator):
        return order_container.get_by_role("button", name="Update")

    @staticmethod
    def _status_badge(order_container: Locator):
        return order_container.locator("span.badge")

    # --- Ações ---

    def navigate_to_orders_page(self):
        expect(self.orders_menu_link).to_be_visible()
        self.orders_menu_link.click()
        expect(self.page).to_have_url(re.compile(r".*/admin/orders"))
        return self

    def find_and_focus_order_container(self, order_id: str):
        container = self._order_container(order_id)
        expect(container).to_be_visible()
        self.current_order = container
        return self

    def select_new_status_for_current_order(self, status: str):
        select = self._status_select(self.current_order)
        expect(select).to_be_visible()
        select.select_option(label=status)
        return self

    def click_update_for_current_order(self):
        button = self._update_button(self.current_order)
        expect(button).to_be_visible()
        with self.page.expect_response(re.compile(r"/admin/orders/")):
            button.click()
        return self

    # --- Asserções ---

    def assert_order_status_for_current_order(self, expected_status: str):
        badge = self._status_badge(self.current_order)
        expect(badge).to_be_visible()
        expect(badge).to_contain_text(expected_status)
        return self
