import re

from playwright.sync_api import Page, expect


class OtpLoginPage:
    def __init__(self, page: Page):
        self.page = page
        self.email_input = page.locator("#email")
        self.send_code_button = page.get_by_role("button", name="Send Code")
        self.code_input = page.locator("#code")
        self.verify_button = page.get_by_role("button", name="Verify")

    def visit_request_page(self):
        self.page.goto("/login/otp")
        return self

    def request_code(self, email: str):
        expect(self.email_input).to_be_visible()
        self.email_input.fill(email)
        self.send_code_button.click()
        return self

    def submit_code(self, code: str):
        expect(self.code_input).to_be_visible()
        self.code_input.fill(code)
        self.verify_button.click()
        return self

    def assert_on_verify_page(self):
        expect(self.page).to_have_url(re.compile(r".*/login/otp/verify"))
        return self
