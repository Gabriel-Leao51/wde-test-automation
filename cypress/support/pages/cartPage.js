class CartPage {
  elements = {
    /** Recebe o nome do produto clicado e o encontra entre os produtos listados no carrinho
     * @param {string} productTitle - Nome do produto a ser verificado no carrinho
     * @returns {Cypress.Chainable<JQuery<HTMLElement>>} - Retorna o elemento encontrado
     */
    productTitleElement: (productTitle) => cy.contains("h2", productTitle),

    /** Botão 'Buy Products' para continuar com o checkout */
    buyProductsButton: () => cy.contains(".btn", "Buy Products"),
  };

  //Ações

  /** Verifica se o produto está listado no carrinho
   * @param {string} productTitle - Nome do produto a ser verificado no carrinho
   * @returns {CartPage} - Retorna a instância da classe CartPage para encadeamento de métodos
   */
  verifyProductInCart(productTitle) {
    this.elements.productTitleElement(productTitle).should("be.visible");
    return this;
  }

  /** Clica no botão 'Buy Products' para continuar com o checkout
   * @returns {CartPage} - Retorna a instância da classe CartPage para encadeamento de métodos
   */
  clickBuyProductsButton() {
    this.elements.buyProductsButton().click();
    return this;
  }
}

export default new CartPage();
