from playwright.sync_api import Page, expect


class LoginPage:
    def __init__(self, page: Page):
        self.page = page
        self.email_input = page.locator("#email")
        self.password_input = page.locator("#password")
        self.login_button = page.locator("form .btn")
        self.error_message = page.locator(".alert")

    def visit(self):
        self.page.goto("/login")
        return self

    def type_email(self, email: str):
        self.email_input.fill(email)
        return self

    def type_password(self, password: str):
        self.password_input.fill(password)
        return self

    def click_login_button(self):
        self.login_button.click()
        return self

    def login(self, email: str, password: str):
        self.visit()
        self.type_email(email)
        self.type_password(password)
        self.click_login_button()
        return self

    def check_error_message(self):
        expect(self.error_message).to_be_visible()
        return self
