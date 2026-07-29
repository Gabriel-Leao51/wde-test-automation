from pytest_bdd import parsers, scenarios, then, when

scenarios("visual/visual_regression.feature")


@when("eu visito a página de login")
def visit_login_page(login_page):
    login_page.visit()


@when("eu visito o catálogo de produtos")
def visit_products_catalog(page):
    page.goto("/products")


@when(parsers.parse('eu visito a página de detalhes do produto "{product_id}"'))
def visit_product_details(page, product_id):
    page.goto(f"/products/{product_id}")


@when("eu visito o painel de gerenciamento de produtos")
def visit_admin_manage_products(page):
    page.goto("/admin/products")


@when("eu tento acessar uma página protegida sem estar logado")
def visit_protected_page_unauthenticated(page):
    page.context.clear_cookies()
    page.goto("/admin/products")


@then(parsers.parse('a página deve corresponder ao snapshot "{snapshot_name}"'))
def assert_page_matches_snapshot(page, assert_snapshot, snapshot_name):
    assert_snapshot(page, name=f"{snapshot_name}.png")
