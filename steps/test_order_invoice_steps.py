import re
from pathlib import Path

from playwright.sync_api import expect
from pytest_bdd import parsers, scenarios, then, when

scenarios("client/order_invoice.feature")


@when('I navigate to the "Orders" page')
def navigate_to_orders_page(page):
    page.locator("#main-header").get_by_role("link", name="Orders").click()
    expect(page).to_have_url(re.compile(r".*/orders$"))


@then('I should see a "Download Invoice" link for my order')
def assert_download_invoice_link_visible(page):
    expect(page.get_by_role("link", name="Download Invoice").first).to_be_visible()


@when('I click the "Download Invoice" link')
def click_download_invoice_link(page, scenario_context):
    with page.expect_download() as download_info:
        page.get_by_role("link", name="Download Invoice").first.click()
    scenario_context["download"] = download_info.value


@then("a PDF file should be downloaded")
def assert_pdf_downloaded(scenario_context):
    download = scenario_context["download"]
    assert download.suggested_filename.endswith(".pdf")
    saved_path = download.path()
    assert saved_path is not None
    assert Path(saved_path).stat().st_size > 0


@when(parsers.parse('I request the invoice for order id "{order_id}"'))
def request_invoice_for_order_id(page, scenario_context, order_id):
    scenario_context["invoice_response"] = page.request.get(f"/orders/{order_id}/invoice.pdf")


@then(parsers.parse("I should receive a {status:d} response"))
def assert_response_status(scenario_context, status):
    assert scenario_context["invoice_response"].status == status
