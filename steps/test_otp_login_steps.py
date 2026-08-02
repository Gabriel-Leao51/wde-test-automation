import re

from playwright.sync_api import expect
from pytest_bdd import given, parsers, scenarios, then, when

scenarios("client/otp_login.feature")


@given("I am on the OTP login request page")
def visit_otp_request_page(otp_login_page):
    otp_login_page.visit_request_page()


@when(parsers.parse('I request a login code for "{email}"'))
def request_login_code(otp_login_page, email):
    otp_login_page.request_code(email)


@then("I should be redirected to the OTP verification page")
@then("I should still be on the OTP verification page")
def assert_on_verify_page(otp_login_page):
    otp_login_page.assert_on_verify_page()


@when(parsers.parse('I retrieve the login code from Mailpit for "{email}"'))
def retrieve_login_code(playwright, mailpit_url, page, scenario_context, email):
    request_context = playwright.request.new_context(base_url=mailpit_url)
    code = None
    try:
        # Mailpit delivers over real SMTP, so the message may not be indexed
        # by its API yet the instant the request page redirects - poll
        # briefly rather than asserting on the very first read.
        for _ in range(10):
            response = request_context.get("/api/v1/messages")
            body = response.json()
            matching = [
                message
                for message in body["messages"]
                if any(recipient["Address"] == email for recipient in message["To"])
                and "Login Code" in message["Subject"]
            ]
            if matching:
                # Mailpit returns newest first, and each code request deletes
                # any prior pending code for the email, so the newest message
                # is always the one that matters.
                detail = request_context.get(f"/api/v1/message/{matching[0]['ID']}").json()
                found = re.search(r"\b(\d{6})\b", detail["Text"])
                if found:
                    code = found.group(1)
                    break
            page.wait_for_timeout(500)
    finally:
        request_context.dispose()

    assert code, f"could not find a login code email for {email} in Mailpit"
    scenario_context["otp_code"] = code


@when("I submit the retrieved login code")
def submit_retrieved_code(otp_login_page, scenario_context):
    otp_login_page.submit_code(scenario_context["otp_code"])


@when(parsers.parse("I submit an incorrect login code {times:d} times"))
def submit_incorrect_code_multiple_times(otp_login_page, times):
    for _ in range(times):
        otp_login_page.submit_code("000000")


@then("I should be logged in")
def assert_logged_in(page):
    expect(page.locator("#main-header").get_by_role("link", name="Orders")).to_be_visible()
