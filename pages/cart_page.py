from playwright.sync_api import Page, expect


class CartPage:
    def __init__(self, page: Page):
        self.page = page
        self.buy_products_button = page.get_by_role("button", name="Buy Products")

    # --- Elementos (parametrizados) ---

    def product_title_element(self, product_title: str):
        return self.page.get_by_role("heading", name=product_title, level=2)

    # --- Ações ---

    def verify_product_in_cart(self, product_title: str):
        expect(self.product_title_element(product_title)).to_be_visible()
        return self

    def click_buy_products_button(self):
        self.buy_products_button.click()
        return self
