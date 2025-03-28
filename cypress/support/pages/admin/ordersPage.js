/**
 * Representa a página de gestão pedidos da aplicação.
 * Encapsula seletores e ações relacionadas ao processo de gestão de pedidos.
 */
class OrdersPage {
  elements = {
    ordersMenuLink: () => cy.contains("a", "Manage Orders"),
    /**
     * Input hidden que contém o orderId.
     * @param {string} orderId - O ID do pedido.
     * @returns {Cypress.Chainable<JQuery<HTMLElement>>}
     */
    _orderIdInput: (orderId) =>
      cy.get(`input[type="hidden"][name="orderid"][value="${orderId}"]`),

    /**
     * Container principal de um pedido específico, encontrado via ID.
     * @param {string} orderId - O ID do pedido.
     * @returns {Cypress.Chainable<JQuery<HTMLElement>>}
     */
    orderContainer: (orderId) => {
      const containerSelector = "article.order-item";
      return this.elements._orderIdInput(orderId).closest(containerSelector);
    },

    /**
     * Dropdown de status DENTRO de um container de pedido específico.
     * @param {JQuery<HTMLElement>} orderContainerElement - O elemento container do pedido (obtido via alias).
     * @returns {Cypress.Chainable<JQuery<HTMLSelectElement>>}
     */
    statusSelect: (orderContainerElement) =>
      cy.wrap(orderContainerElement).find('select[name="status"]'),

    /**
     * Botão 'Update' DENTRO de um container de pedido específico.
     * @param {JQuery<HTMLElement>} orderContainerElement - O elemento container do pedido (obtido via alias).
     * @returns {Cypress.Chainable<JQuery<HTMLButtonElement>>}
     */
    updateButton: (orderContainerElement) =>
      cy
        .wrap(orderContainerElement)
        .find('btn btn-alt, button:contains("Update")'),

    /**
     * Badge/Display de status DENTRO de um container de pedido específico.
     * @param {JQuery<HTMLElement>} orderContainerElement - O elemento container do pedido (obtido via alias).
     * @returns {Cypress.Chainable<JQuery<HTMLElement>>}
     */
    statusBadge: (orderContainerElement) =>
      cy.wrap(orderContainerElement).find("span.badge"),
  };

  // --- Ações ---

  /** Navega para a página de gerenciamento de pedidos. */
  navigateToOrdersPage() {
    this.elements.ordersMenuLink().should("be.visible").click();
    cy.url().should("include", "/admin/orders");
    return this;
  }

  /**
   * Localiza o container do pedido pelo ID e o armazena no alias '@currentOrder'.
   * Nota: Este método configura o contexto (alias) para ações subsequentes.
   * @param {string} orderId - O ID do pedido a ser localizado.
   */
  findAndAliasOrderContainer(orderId) {
    this.elements.orderContainer(orderId).as("currentOrder");
    cy.get("@currentOrder").should("exist").and("be.visible");
  }

  /**
   * Seleciona um novo status no dropdown do pedido atualmente em foco (alias @currentOrder).
   * @param {string} status - O texto da opção a ser selecionada (ex: "Fulfilled").
   */
  selectNewStatusForCurrentOrder(status) {
    cy.get("@currentOrder").then((containerElement) => {
      this.elements
        .statusSelect(containerElement)
        .should("be.visible")
        .select(status);
    });
    return this;
  }

  /**
   * Clica no botão "Update" do pedido atualmente em foco (alias @currentOrder).
   * A espera pela requisição (intercept/wait) deve ser feita no step definition.
   */
  clickUpdateForCurrentOrder() {
    cy.get("@currentOrder").then((containerElement) => {
      this.elements.updateButton(containerElement).should("be.visible").click();
    });
    return this;
  }

  // --- Asserções ---

  /**
   * Verifica se o badge de status dentro do pedido em foco (@currentOrder) exibe o texto esperado.
   * @param {string} expectedStatus - O texto do status esperado (ex: "Fulfilled").
   */
  assertOrderStatusForCurrentOrder(expectedStatus) {
    cy.get("@currentOrder").then((containerElement) => {
      this.elements
        .statusBadge(containerElement)
        .should("be.visible")
        .and("contain.text", expectedStatus);
    });
    return this;
  }
}

export default new OrdersPage();
