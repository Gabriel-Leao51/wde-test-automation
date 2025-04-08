import { Given } from "@badeball/cypress-cucumber-preprocessor";
import loginPage from "../pages/loginPage";

Given("que eu estou logado como {string}", (userType) => {
  const userRole = userType.toLowerCase();

  cy.fixture("users.json").then((allUsers) => {
    const credentials = allUsers[userRole]; // Pega a chave correta (admin ou cliente)

    if (!credentials?.email || !credentials?.password) {
      throw new Error(
        `Credenciais para '${userRole}' não encontradas ou inválidas em users.json`
      );
    }

    loginPage.login(credentials.email, credentials.password);

    // Verificações pós-login condicionais (como antes)
    if (userRole === "administrador") {
      cy.url().should("contain", "/products");
      cy.contains("a", "Manage Products");
    } else if (userRole === "cliente") {
      cy.contains("a", "Orders");
    }
  });
});
