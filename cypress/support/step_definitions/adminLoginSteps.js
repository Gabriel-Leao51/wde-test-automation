import { Given, When, Then } from "@badeball/cypress-cucumber-preprocessor";
import loginPage from "../pages/admin/loginPage";

let adminCredentials;

before(() => {
  cy.fixture("users.json").then((data) => {
    adminCredentials = data;
  });
});

//Cenário: Login com credenciais validas
Given("que eu estou na pagina de login administrativo", () => {
  loginPage.visit();
});

When("eu insiro um email de administrador valido", () => {
  loginPage.typeEmail(adminCredentials.admin.email);
});

When("eu insiro uma senha de administrador valida", () => {
  loginPage.typePassword(adminCredentials.admin.password);
});

When('eu clico no botao de "Login"', () => {
  loginPage.clickLoginButton();
});

Then(
  "eu devo ser redirecionado para a pagina principal do painel administrativo",
  () => {
    cy.url().should("include", "/products");
  }
);

Then(
  "eu devo ver as opcoes de menu {string} e {string}",
  (manageProducts, manageOrders) => {
    cy.contains(manageProducts).should("be.visible");
    cy.contains(manageOrders).should("be.visible");
  }
);

Then("eu devo ver o botao {string} no cabecalho", (logout) => {
  cy.contains(logout).should("be.visible");
});

// Cenário: Login com credenciais invalidas
Given("que eu estou na pagina de login", () => {
  loginPage.visit();
});

When("eu insiro um email invalido", () => {
  loginPage.typeEmail(adminCredentials.invalidAdmin.email);
});

Then("eu insiro uma senha invalida", () => {
  loginPage.typePassword(adminCredentials.invalidAdmin.password);
});

Then('eu clico no botão de "Login"', () => {
  loginPage.clickLoginButton();
});

Then("eu devo ver uma mensagem de erro", (errorMessage) => {
  loginPage.checkErrorMessage(errorMessage);
});

Then("eu devo permanecer na pagina de login", () => {
  cy.url().should("include", "/login");
});
