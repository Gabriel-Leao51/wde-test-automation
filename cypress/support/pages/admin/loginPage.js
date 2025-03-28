/**
 * Representa a página de Login da aplicação.
 * Encapsula seletores e ações relacionadas ao processo de login.
 */
class LoginPage {
  // --- Elementos ---
  elements = {
    /** Campo de input para o email do usuário. */
    emailInput: () => cy.get("#email"),

    /** Campo de input para a senha do usuário. */
    passwordInput: () => cy.get("#password"),

    /** Botão para submeter o formulário de login. */
    loginButton: () => cy.get("form .btn"), // Seletor original

    /** Elemento que exibe mensagens de erro no login. */
    errorMessage: () => cy.get(".alert"), // Seletor original
  };

  // --- Ações ---

  /**
   * Navega diretamente para a página de login da aplicação.
   * @returns {LoginPage} Instância da página para encadeamento.
   */
  visit() {
    cy.visit("/login");
    return this;
  }

  /**
   * Digita o email no campo correspondente.
   * @param {string} email - O email a ser digitado.
   * @returns {LoginPage} Instância da página para encadeamento.
   */
  typeEmail(email) {
    this.elements.emailInput().type(email);
    return this;
  }

  /**
   * Digita a senha no campo correspondente.
   * @param {string} password - A senha a ser digitada.
   * @returns {LoginPage} Instância da página para encadeamento.
   */
  typePassword(password) {
    this.elements.passwordInput().type(password);
    return this;
  }

  /**
   * Clica no botão de login para submeter o formulário.
   * @returns {LoginPage} Instância da página para encadeamento.
   */
  clickLoginButton() {
    this.elements.loginButton().click();
    return this;
  }

  /**
   * Executa o fluxo completo de login: visita a página, preenche email/senha e clica no botão.
   * @param {string} email - O email do usuário.
   * @param {string} password - A senha do usuário.
   * @returns {LoginPage} Instância da página para encadeamento.
   */
  login(email, password) {
    this.visit();
    this.typeEmail(email);
    this.typePassword(password);
    this.clickLoginButton();
    return this;
  }

  // --- Asserções ---

  /**
   * Verifica se a mensagem de erro de login está visível na página.
   * @returns {LoginPage} Instância da página para encadeamento.
   */
  checkErrorMessage() {
    this.elements.errorMessage().should("be.visible");
    return this;
  }
}

export default new LoginPage();
