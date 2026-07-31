import re

from playwright.sync_api import expect
from pytest_bdd import given, parsers, scenarios, then, when

from utils.helpers import format_product_data

scenarios("admin/manage_product.feature")


# --- Background ---


@given(parsers.parse('I am on the admin panel home page "{expected_path}"'))
def assert_on_admin_home_page(page, expected_path):
    expect(page).to_have_url(re.compile(re.escape(expected_path)))


@when(parsers.parse('I navigate to the manage products page "{link_text}"'))
def navigate_to_manage_products(products_page, link_text):
    products_page.click_manage_products_link()


# --- Generic steps reused across scenarios ---


@when(parsers.parse('I click the "{button_text}" button'))
def click_generic_button(page, products_page, button_text):
    if button_text == "Add Product":
        products_page.click_add_new_product_button()
    elif button_text == "Save":
        products_page.click_save_button()
    else:
        locator = page.locator("button, .btn, a.btn").filter(has_text=button_text).first
        expect(locator).to_be_visible()
        locator.click()


@when(parsers.parse('I click the "{button_text}" button for the product titled "{product_title}"'))
def click_button_for_product(products_page, scenario_context, button_text, product_title):
    if button_text == "View & Edit":
        products_page.click_edit_product_button(product_title)
    elif button_text == "Delete":
        scenario_context["deleted_product_id"] = products_page.click_delete_product_button(product_title)
    else:
        raise ValueError(f'Action for the "{button_text}" button is not implemented for products.')


@then(parsers.parse('I should be redirected to the manage products page "{expected_path}"'))
def assert_redirected_to_manage_products(page, expected_path):
    expect(page).to_have_url(re.compile(re.escape(expected_path)))


# --- Steps: Add Product ---


@when("I fill in the add product form with the following data:")
def fill_add_product_form(products_page, datatable):
    product_data = format_product_data(datatable)
    products_page.fill_product_form(product_data)


@then(parsers.parse('the product "{product_title}" should be visible in the product list with title and image'))
def assert_product_added(products_page, product_title):
    products_page.assert_product_added_successfully(product_title)


# --- Steps: Edit Product ---


@when("I fill in the edit product form with the following data:")
def fill_edit_product_form(products_page, datatable):
    product_data = format_product_data(datatable)
    products_page.fill_edit_product_form(product_data)


@then(parsers.parse('the product "{product_title}" should be displayed in the product list with the updated title'))
def assert_product_edited(products_page, product_title):
    products_page.assert_product_edited_successfully(product_title)


# --- Steps: Delete Product ---


@then(parsers.parse('I should see a confirmation dialog to delete "{product_title}"'))
def assert_delete_confirmation_dialog(products_page, product_title):
    products_page.assert_delete_confirmation_dialog_visible(product_title)


@when("I confirm the deletion")
def confirm_deletion(products_page):
    products_page.confirm_delete()


@when("I cancel the deletion")
def cancel_deletion(products_page):
    products_page.cancel_delete()


@then(parsers.parse('the product "{product_title}" should still be displayed in the product list'))
def assert_product_still_displayed(products_page, product_title):
    expect(products_page.product_list_item_title(product_title)).to_be_visible()


@then(parsers.parse('the product "{product_title}" should no longer be displayed in the product list'))
def assert_product_deleted(products_page, scenario_context, product_title):
    products_page.assert_product_deleted_successfully(scenario_context["deleted_product_id"])


# --- Steps: Date Picker ---


@when(parsers.parse('I set the launch date to "{day_aria_label}" using the date picker'))
def set_launch_date(products_page, day_aria_label):
    products_page.set_launch_date(day_aria_label)


@then(parsers.parse('the launch date field should read "{expected_value}"'))
def assert_launch_date_field(products_page, expected_value):
    expect(products_page.product_launch_date_input).to_have_value(expected_value)


# --- Steps: Drag and Drop Image Upload ---


@when(parsers.parse('I drag and drop "{filename}" onto the image upload dropzone'))
def drag_and_drop_image(products_page, filename):
    products_page.drop_image_file(filename)


# --- Steps: Rich Text Editor / XSS Sanitization ---


@when(parsers.parse('I format the product description as bold "{text}"'))
def format_description_bold(products_page, text):
    products_page.format_description_bold(text)


@when(parsers.parse('I set the product description to the raw HTML "{html}"'))
def set_description_html(products_page, html):
    products_page.set_description_html(html)


@when(parsers.parse('I view the customer product page for "{product_title}"'))
def view_customer_product_page(products_page, product_title):
    products_page.view_customer_product_page(product_title)


@then(parsers.parse('the rendered product description should contain bold text "{text}"'))
def assert_description_bold_text(products_page, text):
    expect(products_page.rendered_description.locator("strong")).to_contain_text(text)


@then(parsers.parse('the rendered product description should include the text "{text}"'))
def assert_description_text(products_page, text):
    expect(products_page.rendered_description).to_contain_text(text)


@then(parsers.parse('the rendered product description should not contain a "{tag}" element'))
@then(parsers.parse('the rendered product description should not contain an "{tag}" element'))
def assert_description_lacks_tag(products_page, tag):
    expect(products_page.rendered_description.locator(tag)).to_have_count(0)


@then("the injected script should not have executed")
def assert_script_did_not_execute(page):
    executed = page.evaluate("() => window.xssMarker === true")
    assert not executed, "the sanitizer failed to strip an executable payload"


# --- Steps: Validation (Required Field) ---


@then("I should see an error message stating that required fields must be filled in")
def assert_required_field_error(products_page):
    validity = products_page.product_title_input.evaluate(
        "el => ({ valueMissing: el.validity.valueMissing, message: el.validationMessage })"
    )
    # Native HTML5 validation message wording is browser/locale-specific (e.g. Chromium/Firefox
    # say "Please fill out this field.", WebKit says "Fill out this field") - assert the
    # behavior (blocked due to a missing required value, with some message shown), not the
    # exact text.
    assert validity["valueMissing"] is True
    assert validity["message"] != ""


@then("I should remain on the add product page")
def assert_still_on_new_product_page(page):
    expect(page).to_have_url(re.compile(r".*/admin/products/new"))
