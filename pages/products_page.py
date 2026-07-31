import base64
import mimetypes
import re
from datetime import datetime
from pathlib import Path

from playwright.sync_api import Page, expect

TEST_DATA_DIR = Path(__file__).resolve().parent.parent / "test_data"


class ProductsPage:
    def __init__(self, page: Page):
        self.page = page
        self.header = page.locator("#main-header")
        self.manage_products_link = self.header.get_by_role("link", name="Manage Products")
        self.add_new_product_button = page.locator("main").get_by_role("link", name="Add Product")
        self.product_title_input = page.locator("#title")
        self.product_image_input = page.locator("#image")
        self.image_dropzone = page.locator("#image-upload-control")
        self.image_preview = page.locator("#image-upload-control img")
        self.product_summary_input = page.locator("#summary")
        self.product_price_input = page.locator("#price")
        self.product_department_select = page.locator("#department")
        self.product_launch_date_input = page.locator("#launchDate")
        self.product_description_input = page.locator("#description")
        self.save_button = page.get_by_role("button", name="Save")
        self.add_to_cart_button = page.get_by_role("button", name="Add to Cart")
        self.delete_confirm_dialog = page.locator("#delete-confirm-dialog")
        self.delete_confirm_button = page.locator("#delete-confirm-button")
        self.delete_cancel_button = page.locator("#delete-cancel-button")

    # --- Elements (parameterized) ---

    def product_list_item(self, product_title: str):
        return self.page.locator("article.product-item").filter(has_text=product_title)

    def product_list_item_title(self, product_title: str):
        return self.product_list_item(product_title).locator("h2")

    def product_list_item_image(self, product_title: str):
        return self.product_list_item(product_title).locator("img")

    def edit_product_button(self, product_title: str):
        return self.product_list_item(product_title).get_by_role("link", name="View & Edit")

    def delete_product_button(self, product_title: str):
        return self.product_list_item(product_title).get_by_role("button", name="Delete")

    def view_details_button(self, product_title: str):
        return self.product_list_item(product_title).get_by_role("link", name="View Details")

    # --- Actions ---

    def click_manage_products_link(self):
        expect(self.manage_products_link).to_be_visible()
        self.manage_products_link.click()
        expect(self.page).to_have_url(re.compile(r".*/admin/products$"))
        return self

    def click_add_new_product_button(self):
        expect(self.add_new_product_button).to_be_visible()
        self.add_new_product_button.click()
        expect(self.page).to_have_url(re.compile(r".*/admin/products/new"))
        return self

    def fill_product_form(self, product_data: dict[str, str]):
        field_map = {
            "title": self.product_title_input,
            "summary": self.product_summary_input,
            "price": self.product_price_input,
            "description": self.product_description_input,
        }

        for field, value in product_data.items():
            if field == "image":
                self.product_image_input.set_input_files(str(TEST_DATA_DIR / value))
                continue

            if field == "department":
                self.product_department_select.select_option(str(value))
                continue

            locator = field_map.get(field)
            if locator is None:
                continue

            expect(locator).to_be_visible()
            locator.fill(str(value))

        return self

    def fill_edit_product_form(self, product_data: dict[str, str]):
        return self.fill_product_form(product_data)

    def set_launch_date(self, day_aria_label: str):
        # Opens the self-hosted flatpickr widget and clicks a real, locatable
        # day cell - not a native <input type="date"> picker, which Playwright
        # (and most automation tools) can't drive consistently across browsers.
        # flatpickr opens on today's month when the field is empty, so the
        # calendar must be navigated to the target month/year first rather
        # than assuming the target day is already visible.
        target = datetime.strptime(day_aria_label, "%B %d, %Y")
        self.product_launch_date_input.click()
        self.page.get_by_role("combobox", name="Month").select_option(label=target.strftime("%B"))
        year_input = self.page.get_by_role("spinbutton", name="Year")
        year_input.fill(str(target.year))
        year_input.press("Enter")
        day_cell = self.page.locator(f'.flatpickr-day[aria-label="{day_aria_label}"]')
        expect(day_cell).to_be_visible()
        day_cell.click()
        return self

    def drop_image_file(self, filename: str):
        # Playwright has no built-in "drop a file" helper (unlike set_input_files
        # for the native file-picker path), so the drop is simulated in-page: a
        # real File is built from the fixture's bytes and dispatched as a native
        # DragEvent, exercising the same dropzone code the browser would use for
        # an actual drag-and-drop.
        file_path = TEST_DATA_DIR / filename
        encoded = base64.b64encode(file_path.read_bytes()).decode("ascii")
        mime_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"

        self.image_dropzone.evaluate(
            """(element, { data, fileName, mimeType }) => {
                const binary = atob(data);
                const bytes = new Uint8Array(binary.length);
                for (let i = 0; i < binary.length; i++) {
                    bytes[i] = binary.charCodeAt(i);
                }
                const file = new File([bytes], fileName, { type: mimeType });
                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(file);
                element.dispatchEvent(new DragEvent('drop', { dataTransfer, bubbles: true, cancelable: true }));
            }""",
            {"data": encoded, "fileName": filename, "mimeType": mime_type},
        )
        return self

    def click_save_button(self):
        expect(self.save_button).to_be_visible()
        self.save_button.click()
        return self

    def click_edit_product_button(self, product_title: str):
        button = self.edit_product_button(product_title)
        expect(button).to_be_visible()
        button.click()
        expect(self.page).to_have_url(re.compile(r".*/admin/products/(?!new)"))
        return self

    def click_delete_product_button(self, product_title: str) -> str:
        button = self.delete_product_button(product_title)
        expect(button).to_be_visible()
        product_id = button.get_attribute("data-productid")
        if not product_id:
            raise ValueError(
                f'Could not find the "data-productid" attribute on the Delete button '
                f'for the product "{product_title}".'
            )
        button.click()
        return product_id

    def confirm_delete(self):
        expect(self.delete_confirm_button).to_be_visible()
        self.delete_confirm_button.click()
        return self

    def cancel_delete(self):
        expect(self.delete_cancel_button).to_be_visible()
        self.delete_cancel_button.click()
        return self

    def click_view_details_button(self, product_title: str):
        button = self.view_details_button(product_title)
        expect(button).to_be_visible()
        button.click()
        expect(self.page.get_by_role("heading", name=product_title, level=1)).to_be_visible()
        return self

    def click_add_to_cart_button(self):
        expect(self.add_to_cart_button).to_be_visible()
        self.add_to_cart_button.click()
        return self

    # --- Assertions ---

    def assert_product_added_successfully(self, product_title: str):
        expect(self.page).to_have_url(re.compile(r".*/admin/products"))
        expect(self.product_list_item_title(product_title)).to_be_visible()
        expect(self.product_list_item_title(product_title)).to_contain_text(product_title)
        expect(self.product_list_item_image(product_title)).to_be_visible()
        return self

    def assert_product_edited_successfully(self, product_title: str):
        expect(self.page).to_have_url(re.compile(r".*/admin/products"))
        expect(self.product_list_item_title(product_title)).to_be_visible()
        expect(self.product_list_item_title(product_title)).to_contain_text(product_title)
        return self

    def assert_product_deleted_successfully(self, product_id: str):
        expect(self.page.locator(f'[data-productid="{product_id}"]')).to_have_count(0)
        return self

    def assert_delete_confirmation_dialog_visible(self, product_title: str):
        expect(self.delete_confirm_dialog).to_be_visible()
        expect(self.delete_confirm_dialog).to_contain_text(product_title)
        return self
