import { Given, When, Then } from "@badeball/cypress-cucumber-preprocessor";
import ordersPage from "../pages/ordersPage";

// --- Contexto ---

Then("eu navego para a pagina de gerenciamento de pedidos", () => {
  ordersPage.navigateToOrdersPage();
});

// --- Cenário ---

Given("que um pedido com status {string} conhecido existe", () => {
  cy.fixture("orders.json").then((jsonData) => {
    const orderIdFromFixture = jsonData.orderData?.testOrderId;
    if (!orderIdFromFixture) {
      throw new Error(
        "Fixture 'orders.json' com formato inválido ou 'testOrderId' não encontrado. Esperado: { orderData: { testOrderId: '...' } }"
      );
    }
    this.orderId = orderIdFromFixture;
    cy.log(`Order ID conhecido: ${this.orderId}`);
  });
});

When("eu localizo o pedido conhecido na lista de pedidos", () => {
  if (!this.orderId) {
    throw new Error(
      "Order ID não foi carregado/definido no contexto do teste."
    );
  }
  ordersPage.findAndAliasOrderContainer(this.orderId);
});

Then("eu seleciono o novo status {string} para este pedido", (newStatus) => {
  ordersPage.selectNewStatusForCurrentOrder(newStatus);
});

Then("eu clico no botao {string} deste pedido", (buttonText) => {
  if (buttonText.toLowerCase() === "update") {
    cy.intercept("PATCH", `/admin/orders/${this.orderId}`).as("updateStatus");
    ordersPage.clickUpdateForCurrentOrder();
  } else {
    throw new Error(
      `Ação para o botão "${buttonText}" não implementada para pedidos.`
    );
  }
  cy.wait("@updateStatus");
});

Then(
  "o status {string} deve ser exibido para este pedido",
  (expectedStatus) => {
    ordersPage.assertOrderStatusForCurrentOrder(expectedStatus);
  }
);
