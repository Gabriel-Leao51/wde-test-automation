import { When, Then } from "@badeball/cypress-cucumber-preprocessor";
import productsPage from "../pages/productsPage";
import { formatProductData } from "../../utils/helpers";

When(
  "eu estou na pagina inicial do painel administrativo {string}",
  (expectedPath) => {
    cy.url().should("include", expectedPath);
  }
);

When("eu navego para a pagina de gerenciamento de produtos {string}", () => {
  productsPage.clickManageProductsLink();
});

// --- Common/Reusable Steps
When("eu clico no botao {string}", (buttonText) => {
  if (buttonText === "Add Product") {
    productsPage.clickAddNewProductButton();
  } else if (buttonText === "Save") {
    productsPage.clickSaveButton();
  } else {
    cy.contains("button, .btn, a.btn", buttonText).should("be.visible").click();
    cy.log(`Clicked generic button: ${buttonText}`);
  }
});

When(
  "eu clico no botao {string} para o produto de titulo {string}",
  (buttonText, productTitle) => {
    cy.log(`Clicking "${buttonText}" for product "${productTitle}"`);
    if (buttonText === "View & Edit") {
      productsPage.clickEditProductButton(productTitle);
    } else if (buttonText === "Delete") {
      productsPage.clickDeleteProductButton(productTitle);
    } else {
      throw new Error(
        `Button action "${buttonText}" not recognized in this step definition.`
      );
    }
  }
);

Then(
  "eu devo ser redirecionado para a pagina de gerenciamento de produtos {string}",
  (expectedUrlPath) => {
    cy.url().should("include", expectedUrlPath);
  }
);

// --- Steps: Adicionar Produto ---
When(
  "eu preencho o formulario de adicionar produto com os seguintes dados:",
  (dataTable) => {
    const productDataFormatted = formatProductData(dataTable.rawTable);
    productsPage.fillProductForm(productDataFormatted);
  }
);

Then(
  "o produto {string} deve estar visivel na listagem de produtos com titulo e imagem",
  (productTitle) => {
    productsPage.assertProductAddedSuccessfully({ title: productTitle }); // Novo método no Page Object
  }
);

// --- Steps: Editar Produto ---
When(
  "eu preencho o formulario de edição de produto com os seguintes dados:",
  (dataTable) => {
    const productDataFormatted = formatProductData(dataTable.rawTable);
    productsPage.fillEditProductForm(productDataFormatted);
  }
);

Then(
  "o produto {string} deve ser exibido na listagem de produtos com o titulo atualizado",
  (productTitle) => {
    productsPage.assertProductEditedSuccessfully({ title: productTitle });
  }
);

// --- Steps: Excluir Produto ---
Then(
  "o produto {string} não deve ser mais exibido na listagem de produtos",
  (productTitle) => {
    productsPage.assertProductDeletedSuccessfully(productTitle);
  }
);

// --- Steps: Validação (Campo Obrigatório) ---
Then(
  "eu devo ver uma mensagem de erro informando que os campos obrigatorios devem ser preenchidos",
  () => {
    productsPage.elements.productTitleInput().then(($input) => {
      expect($input[0].validity.valid).to.be.false;

      expect($input[0].validationMessage).to.equal(
        "Please fill out this field."
      );
    });
  }
);
Then("eu devo permanecer na pagina de adicionar produto", () => {
  cy.url().should("include", "/admin/products/new");
});
