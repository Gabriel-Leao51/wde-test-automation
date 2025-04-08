class ProductsPage {
  // --- Elementos ---
  elements = {
    /** Link 'Manage Products' no menu de navegação. */
    manageProductsLink: () => cy.contains("a", "Manage Products"), // Ajuste se o seletor for diferente

    /** Botão 'Add Product' para iniciar a criação de um novo produto. */
    addNewProductButton: () => cy.contains(".btn", "Add Product"), // Ajuste se o seletor for diferente

    /** O elemento <form> usado para criar ou editar produtos. */
    productForm: () => cy.get('form[action^="/admin/products"]'),

    /** Campo de input para o título (nome) do produto. */
    productTitleInput: () => cy.get("#title"),

    /** Campo de input do tipo 'file' para a imagem do produto. */
    productImageInput: () => cy.get("#image"),

    /** Campo de input para o resumo (descrição curta) do produto. */
    productSummaryInput: () => cy.get("#summary"),

    /** Campo de input para o preço do produto. */
    productPriceInput: () => cy.get("#price"),

    /** Campo de textarea para a descrição detalhada do produto. */
    productDescriptionInput: () => cy.get("#description"),

    /** Botão 'Save' no formulário de criação/edição de produto. */
    saveButton: () => cy.contains(".btn", "Save"),

    /** Botão 'Add to Cart na página de detalhes do produto */
    addToCartButton: () => cy.contains(".btn", "Add to Cart"),

    /**
     * Obtém o elemento container principal de um item na lista de produtos, buscando pelo título.
     * @param {string} productTitle - O título do produto a ser localizado.
     * @returns {Cypress.Chainable<JQuery<HTMLElement>>}
     */
    productListItem: (productTitle) =>
      cy.contains(".product-item", productTitle), // Ajuste .product-item se necessário

    /**
     * Obtém o elemento <h2> contendo o título de um item na lista de produtos.
     * @param {string} productTitle - O título do produto a ser localizado.
     * @returns {Cypress.Chainable<JQuery<HTMLHeadingElement>>}
     */
    productListItemTitle: (productTitle) =>
      cy.contains(".product-item-content", productTitle).find("h2"), // Ajuste .product-item-content se necessário

    /**
     * Obtém o elemento <img> de um item na lista de produtos.
     * @param {string} productTitle - O título do produto a ser localizado.
     * @returns {Cypress.Chainable<JQuery<HTMLImageElement>>}
     */
    productListItemImage: (productTitle) =>
      cy.contains(".product-item", productTitle).find("img"), // Ajuste .product-item se necessário

    /**
     * Obtém o botão/link 'View & Edit' para um produto específico na lista.
     * A implementação atual busca pelo texto do título (h2) e navega para os botões irmãos.
     * @param {string} productTitle - O título do produto.
     * @returns {Cypress.Chainable<JQuery<HTMLElement>>} - O elemento do botão/link 'View & Edit'.
     */
    editProductButton: (productTitle) =>
      cy
        .contains("h2", productTitle) // Encontra o H2 com o título
        .siblings(".product-item-actions") // Vai para o container de ações irmão
        .find('a:contains("View & Edit")'), // Encontra o link de edição dentro das ações

    /**
     * Obtém o botão 'Delete' para um produto específico na lista.
     * A implementação atual busca pelo texto do título (h2) e navega para os botões irmãos.
     * Assume que o botão delete tem um atributo 'data-productid'.
     * @param {string} productTitle - O título do produto.
     * @returns {Cypress.Chainable<JQuery<HTMLButtonElement>>} - O elemento do botão 'Delete'.
     */
    deleteProductButton: (productTitle) =>
      cy
        .contains("h2", productTitle) // Encontra o H2 com o título
        .siblings(".product-item-actions") // Vai para o container de ações irmão
        .find('button:contains("Delete")'), // Encontra o botão delete dentro das ações

    /**
     * Obtém o botão 'View Details' para um produto específico na lista.
     * A implementação atual busca pelo texto do título (h2) e navega para os botões irmãos.
     * @param {string} productTitle - O título do produto.
     * @returns {Cypress.Chainable<JQuery<HTMLButtonElement>>} - O elemento do botão 'Delete'.
     */
    viewDetailsButton: (productTitle) =>
      cy
        .contains("h2", productTitle) // Encontra o H2 com o título
        .siblings(".product-item-actions") // Vai para o container de ações irmão
        .find('a:contains("View Details")'), // Encontra o link de detalhes dentro das ações
  };

  // --- Ações ---

  /**
   * Clica no link 'Manage Products' na navegação e verifica a URL.
   * @returns {ProductsPage} Instância da página para encadeamento.
   */
  clickManageProductsLink() {
    this.elements.manageProductsLink().should("be.visible").click();
    cy.url().should("include", "/admin/products");
    return this;
  }

  /**
   * Clica no botão 'Add Product' e verifica a URL da página de novo produto.
   * @returns {ProductsPage} Instância da página para encadeamento.
   */
  clickAddNewProductButton() {
    this.elements.addNewProductButton().should("be.visible").click();
    cy.url().should("include", "/admin/products/new");
    return this;
  }

  /**
   * Preenche o formulário de criação de produto com base nos dados fornecidos.
   * Utiliza um mapa interno para determinar como preencher cada campo (type, selectFile).
   * @param {object} productData - Objeto contendo os dados do produto. Ex: { title: '...', image: '...', price: ..., ... }
   * @returns {ProductsPage} Instância da página para encadeamento.
   */
  fillProductForm(productData) {
    const fieldMap = {
      title: { element: this.elements.productTitleInput, action: "type" },
      image: {
        element: this.elements.productImageInput,
        action: "selectFile",
        options: { force: true },
        prefix: "cypress/fixtures/",
      },
      summary: { element: this.elements.productSummaryInput, action: "type" },
      price: {
        element: this.elements.productPriceInput,
        action: "type",
        transform: String,
      },
      description: {
        element: this.elements.productDescriptionInput,
        action: "type",
      },
    };

    Object.keys(productData).forEach((key) => {
      const config = fieldMap[key];
      if (config) {
        let value = productData[key];
        if (config.transform) {
          value = config.transform(value);
        }
        const elementChain = config.element().should("be.visible"); // Adiciona verificação de visibilidade
        if (config.action === "type") {
          elementChain.clear().type(value); // Adiciona .clear() para consistência e evitar texto acumulado
        } else if (config.action === "selectFile") {
          const filePath = config.prefix ? `${config.prefix}${value}` : value;
          elementChain.selectFile(filePath, config.options || {});
        }
        cy.log(`Campo '${key}' preenchido.`);
      } else {
        cy.log(
          `AVISO: Campo '${key}' fornecido nos dados, mas não mapeado em fillProductForm.`
        );
      }
    });
    return this;
  }

  /**
   * Clica no botão 'Save' do formulário.
   * @returns {ProductsPage} Instância da página para encadeamento.
   */
  clickSaveButton() {
    this.elements.saveButton().should("be.visible").click();
    return this;
  }

  /**
   * Clica no botão 'View & Edit' de um produto específico na lista.
   * @param {string} productTitle - O título do produto a ser editado.
   * @returns {ProductsPage} Instância da página para encadeamento.
   */
  clickEditProductButton(productTitle) {
    this.elements.editProductButton(productTitle).should("be.visible").click();
    cy.url().should("include", "/admin/products/"); // Verifica se foi para uma página de edição
    cy.url().should("not.include", "/admin/products/new"); // Garante que não é a página 'new'
    return this;
  }

  /**
   * Preenche o formulário de EDIÇÃO de produto. Inclui .clear() antes de .type().
   * NOTA: Reutiliza a lógica de `fillProductForm` internamente para evitar duplicação.
   * Se houver campos que SÓ existem na edição, ou precisam de tratamento diferente,
   * a lógica em `fillProductForm` precisaria ser ajustada ou este método ser diferente.
   * @param {object} productData - Objeto contendo os dados atualizados do produto.
   * @returns {ProductsPage} Instância da página para encadeamento.
   */
  fillEditProductForm(productData) {
    // Chama fillProductForm, que agora inclui .clear() em campos 'type'
    this.fillProductForm(productData);
    return this;
  }

  /**
   * Clica no botão 'Delete' de um produto específico, intercepta a requisição DELETE
   * e armazena o ID do produto e a request em aliases.
   * @param {string} productTitle - O título do produto a ser deletado.
   * @returns {ProductsPage} Instância da página para encadeamento.
   */
  clickDeleteProductButton(productTitle) {
    this.elements
      .deleteProductButton(productTitle)
      .should("be.visible")
      .invoke("attr", "data-productid") // Assume que o botão tem 'data-productid'
      .then((productId) => {
        if (!productId) {
          throw new Error(
            `Não foi possível encontrar o atributo 'data-productid' no botão Delete para o produto "${productTitle}". Verifique o seletor e o HTML.`
          );
        }
        cy.wrap(productId).as("deletedProductId"); // Alias para o ID

        // 1. Definir o Intercept ANTES da ação
        cy.intercept("DELETE", `/admin/products/${productId}`).as(
          "deleteProductRequest"
        );

        // 2. Clicar no botão que dispara a request
        // Busca novamente pelo botão usando o ID para garantir que clicamos no correto
        cy.get(`button[data-productid="${productId}"]`).click();
      });
    return this; // Retorna imediatamente, a espera pela request fica no step definition
  }

  /**
   * Clica no botão 'View Details' de um produto específico na lista.
   * @param {string} productTitle - O título do produto a ser editado.
   * @returns {ProductsPage} Instância da página para encadeamento.
   */
  clickViewDetailsButton(productTitle) {
    this.elements.viewDetailsButton(productTitle).should("be.visible").click();
    cy.contains("h1", productTitle); // Verifica se foi para a página de detalhes do produto correto
    return this;
  }

  /**
   * Clica no botão 'Add to Cart' de um produto específico na lista.
   * @param {string} productTitle - O título do produto a ser editado.
   * @returns {ProductsPage} Instância da página para encadeamento.
   */
  clickAddToCartButton() {
    this.elements.addToCartButton().should("be.visible").click();
    return this;
  }

  // --- Asserções ---

  /**
   * Verifica se um produto recém-adicionado está visível na lista (título e imagem) e se a URL está correta.
   * @param {object} productData - Objeto com dados do produto, requer pelo menos `title`.
   * @returns {ProductsPage} Instância da página para encadeamento.
   */
  assertProductAddedSuccessfully(productData) {
    cy.url().should("include", "/admin/products");
    this.elements
      .productListItemTitle(productData.title)
      .should("be.visible")
      .and("contain", productData.title);
    this.elements.productListItemImage(productData.title).should("be.visible");
    return this;
  }

  /**
   * Verifica se um produto editado exibe o título atualizado na lista e se a URL está correta.
   * @param {object} productData - Objeto com dados do produto, requer pelo menos `title` (o título atualizado).
   * @returns {ProductsPage} Instância da página para encadeamento.
   */
  assertProductEditedSuccessfully(productData) {
    cy.url().should("include", "/admin/products");
    this.elements
      .productListItemTitle(productData.title)
      .should("be.visible")
      .and("contain", productData.title);
    // Poderia adicionar verificação de outros campos se eles fossem visíveis na lista
    return this;
  }

  /**
   * Verifica se o produto deletado não existe mais na lista, usando o alias '@deletedProductId'.
   * Assume que o step definition já esperou pela conclusão da request DELETE.
   * @returns {ProductsPage} Instância da página para encadeamento.
   */
  assertProductDeletedSuccessfully() {
    // Espera que o alias exista (foi setado em clickDeleteProductButton)
    cy.get("@deletedProductId").then((deletedProductId) => {
      // Verifica que nenhum elemento com esse data-attribute existe mais no DOM
      cy.get(`[data-productid="${deletedProductId}"]`).should("not.exist");
      // Poderia também verificar se o item da lista com o título não existe mais,
      // mas usar o ID é geralmente mais robusto se títulos puderem se repetir temporariamente.
      // cy.contains('.product-item', previousTitle).should('not.exist'); // Requereria guardar o título anterior
    });
    return this;
  }
}

export default new ProductsPage();
