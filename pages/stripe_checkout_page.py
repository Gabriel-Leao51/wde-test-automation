from playwright.sync_api import Page

TEST_CARD_NUMBER = "4242424242424242"
TEST_CARD_EXPIRY = "12/34"
TEST_CARD_CVC = "123"


class StripeCheckoutPage:
    """Stripe's hosted Checkout page (checkout.stripe.com). Note this is a
    third-party page, not part of the WDE app - the card fields render
    directly in the top-level document (not a cross-origin iframe), which is
    what makes filling them out straightforward in Playwright.
    """

    def __init__(self, page: Page):
        self.page = page

    @property
    def email_input(self):
        return self.page.locator("#email")

    @property
    def card_number_input(self):
        return self.page.locator("#cardNumber")

    @property
    def card_expiry_input(self):
        return self.page.locator("#cardExpiry")

    @property
    def card_cvc_input(self):
        return self.page.locator("#cardCvc")

    @property
    def billing_name_input(self):
        return self.page.locator("#billingName")

    @property
    def submit_button(self):
        return self.page.get_by_test_id("hosted-payment-submit-button")

    def pay_with_test_card(self, email: str, billing_name: str):
        self.email_input.fill(email)
        self.card_number_input.fill(TEST_CARD_NUMBER)
        self.card_expiry_input.fill(TEST_CARD_EXPIRY)
        self.card_cvc_input.fill(TEST_CARD_CVC)
        self.billing_name_input.fill(billing_name)
        self.submit_button.click()
        return self
