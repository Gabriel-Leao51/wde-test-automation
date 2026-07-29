from pytest_bdd import parsers, scenarios, then, when

scenarios("visual/visual_regression.feature")


@when("I visit the login page")
def visit_login_page(login_page):
    login_page.visit()


@when("I visit the product catalog")
def visit_products_catalog(page):
    page.goto("/products")


@when(parsers.parse('I visit the product details page "{product_id}"'))
def visit_product_details(page, product_id):
    page.goto(f"/products/{product_id}")


@when("I visit the manage products panel")
def visit_admin_manage_products(page):
    page.goto("/admin/products")


@when("I try to access a protected page without being logged in")
def visit_protected_page_unauthenticated(page):
    page.context.clear_cookies()
    page.goto("/admin/products")


@then(parsers.parse('the page should match the "{snapshot_name}" snapshot'))
def assert_page_matches_snapshot(page, assert_snapshot, snapshot_name):
    assert_snapshot(page, name=f"{snapshot_name}.png")
