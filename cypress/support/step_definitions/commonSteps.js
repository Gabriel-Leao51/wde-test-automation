import { Given } from "@badeball/cypress-cucumber-preprocessor";
import loginPage from "../pages/admin/loginPage";

Given("que eu estou logado como um administrador", () => {
  cy.fixture("admin_credentials.json").then((data) => {
    const adminCredentials = data;
    if (!adminCredentials?.admin?.email || !adminCredentials?.admin?.password) {
      throw new Error(
        "Fixture 'admin_credentials.json' não encontrada ou formato inválido."
      );
    }
    loginPage.login(
      adminCredentials.admin.email,
      adminCredentials.admin.password
    );

    cy.url().should("contain", "/products");
  });
});
