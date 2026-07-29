import re

from playwright.sync_api import expect
from pytest_bdd import parsers, scenarios, then, when

scenarios("client/purchase_flow.feature")


@when(parsers.parse('I click "View Details" for the product "{product_title}"'))
def click_view_details(products_page, product_title):
    products_page.click_view_details_button(product_title)


@when('I click the "Add to Cart" button on the product details page')
def click_add_to_cart(products_page):
    products_page.click_add_to_cart_button()


@then(parsers.parse('the cart indicator in the navigation bar should be updated to "{expected_count}"'))
def assert_cart_indicator(page, expected_count):
    badge = page.locator("#main-header").locator(".nav-items a", has_text="Cart").locator("span.badge")
    expect(badge).to_have_text(expected_count)


@when(parsers.parse('I click the "{link_text}" link in the navigation bar'))
def click_nav_link(page, link_text):
    page.locator("#main-header .nav-items a").filter(has_text=link_text).first.click()


@then(parsers.parse('I should see the product "{product_title}" listed in the cart'))
def assert_product_in_cart(cart_page, product_title):
    cart_page.verify_product_in_cart(product_title)


@when('I click the "Buy Products" button')
def click_buy_products(cart_page):
    cart_page.click_buy_products_button()


@then("I should be redirected to the external Stripe payment page")
def assert_redirected_to_stripe(page):
    expect(page).to_have_url(re.compile(r"checkout\.stripe\.com"), timeout=20000)


@when("I fill in the Stripe test card details and confirm payment")
def pay_with_stripe_test_card(stripe_checkout_page):
    stripe_checkout_page.pay_with_test_card(
        email="test-customer@example.com", billing_name="Test Customer"
    )


@then("I should be redirected to the order success page")
def assert_redirected_to_order_success(page):
    expect(page).to_have_url(re.compile(r".*/orders/success"), timeout=20000)
