import { When, Then } from "@badeball/cypress-cucumber-preprocessor";

import productsPage from "../pages/productsPage";
import cartPage from "../pages/cartPage";

When('eu clico em "View Details" para o produto {string}', (productTitle) => {
  productsPage.clickViewDetailsButton(productTitle);
});

When('eu clico no botão "Add to Cart" na página de detalhes do produto', () => {
  productsPage.clickAddToCartButton();
});

Then(
  "o indicador do carrinho na barra de navegação deve ser atualizado para {string}",
  (expectedCount) => {
    cy.contains("a", "Cart")
      .find("span.badge")
      .should("have.text", expectedCount);
  }
);

When("eu clico no link {string} da barra de navegação", (linkText) => {
  cy.get(".nav-items a").contains(linkText).click();
});

Then("eu devo ver o produto {string} listado no carrinho", (productTitle) => {
  cartPage.verifyProductInCart(productTitle);
});

When('eu clico no botão "Buy Products"', () => {
  cartPage.clickBuyProductsButton();
});

Then(
  "eu devo ser redirecionado para a página de pagamento externa do Stripe",
  () => {
    cy.log("Verificando redirecionamento para Stripe usando cy.origin...");

    // Usa cy.origin para executar a asserção de URL no domínio de destino
    cy.origin("https://checkout.stripe.com", () => {
      // Dentro deste bloco, 'cy' opera no contexto de checkout.stripe.com

      cy.log("[cy.origin] Executando dentro de checkout.stripe.com.");

      // Verifica a URL DENTRO da origem do Stripe.
      // cy.url() aqui vai esperar a navegação para esta origem completar.
      // Aumentamos o timeout para dar conta da navegação cross-origin.
      cy.url({ timeout: 20000 }) // Timeout de 20 segundos para a URL carregar
        .should("include", "checkout.stripe.com"); // Confirma que estamos no domínio correto

      cy.log("[cy.origin] Asserção cy.url() passou com sucesso.");

      // NOTA: Não tentaremos interagir com elementos aqui (sem .get, .type, .click)
      // pois sabemos que o Cypress tem dificuldade em selecioná-los nesta página específica.
      // A verificação da URL é suficiente para este teste.
    });

    // Este log executa DEPOIS que o bloco cy.origin terminou com sucesso
    cy.log("Verificação de redirecionamento para Stripe concluída.");
  }
);
