import { When, Then } from "@badeball/cypress-cucumber-preprocessor";

When("eu tento acessar a URL {string} sem estar logado", (path) => {
  cy.clearCookies();
  cy.clearLocalStorage();
  cy.visit(path, { failOnStatusCode: false });
});

Then("eu devo ser direcionado para a página de erro 401", () => {
  cy.url().should("include", "/401");
});

Then("eu devo ver os elementos da página de não autenticado", () => {
  cy.get("h1").contains("Not authenticated!").should("be.visible");

  cy.contains("You are not authenticated!").should("be.visible");
  cy.contains("button, a", "Back to safety!", { matchCase: false }).should(
    "be.visible"
  );
});

When("eu tento acessar a URL {string}", (path) => {
  cy.visit(path, { failOnStatusCode: false });
});

Then("eu devo ver uma mensagem indicando falta de autorização", () => {
  cy.contains("Not authorized - you are not authorized to access this page!", {
    matchCase: false,
  }).should("be.visible");
  cy.url().should("not.match", /\/admin\/(products|orders)\/\d+/);
  cy.url().should("not.match", /\/admin\/(products|orders)\/new/);
});

Then("eu NÃO devo conseguir acessar a página de Produtos do Admin", () => {
  cy.log(
    "VERIFICANDO BUG: Espera-se NÃO encontrar elementos da pág. Produtos Admin"
  );

  cy.get('a[href*="/admin/products/new"]').should("not.exist");
  cy.get("h2")
    .contains("Manage Products", { matchCase: false })
    .should("not.exist");
});

Then("eu NÃO devo conseguir acessar o formulário de Edição de Produto", () => {
  cy.log(
    "VERIFICANDO BUG: Espera-se NÃO encontrar elementos do form Edição Produto"
  );

  cy.get("button").contains("Save", { matchCase: false }).should("not.exist");
});
