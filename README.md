# Automação de Testes (Portfólio QA) - WDE Shop

![Status CI](https://github.com/Gabriel-Leao51/wde-test-automation/actions/workflows/cypress-tests.yml/badge.svg)

## 1. Introdução

Este repositório contém um projeto de automação de testes E2E (End-to-End) desenvolvido como parte de um portfólio de Quality Assurance (QA). O objetivo principal foi construir uma suíte de testes robusta utilizando tecnologias modernas e boas práticas de mercado, demonstrando habilidades em automação, BDD, CI/CD e identificação de bugs.

A aplicação alvo (AUT - Application Under Test) é a **WDE Shop**, um e-commerce fictício hospedado em: `https://wde-5p3f.onrender.com`.

## 2. Escopo da Automação

O projeto abrange diferentes áreas e tipos de testes:

- **Testes Funcionais (Painel Administrativo):**
  - **Login:** Autenticação no painel administrativo.
  - **Gerenciamento de Produtos:** CRUD completo (Adicionar, Editar, Excluir) - Caminho Feliz.
  - **Gerenciamento de Produtos:** Validação de campo obrigatório (Nome/Título) - Caminho Infeliz.
  - **Gerenciamento de Pedidos:** Alteração do status de um pedido existente.
- **Testes de Segurança (Painel Administrativo):**
  - **Autenticação:** Tentativas de acesso a áreas administrativas por usuários não logados.
  - **Autorização:** Tentativas de acesso a áreas administrativas por usuários logados com perfil de "cliente" (não autorizado).
- **Teste E2E (Fluxo do Cliente):**
  - **Jornada de Compra:** Login do cliente, busca de produto, adição ao carrinho, visualização do carrinho e redirecionamento para a página de pagamento (Stripe).

## 3. Tecnologias e Metodologias Utilizadas

- **Framework de Automação:** [Cypress](https://www.cypress.io/)
- **Linguagem:** JavaScript (Node.js)
- **Abordagem BDD:** Gherkin (PT-BR) com [Cucumber](https://cucumber.io/) via `@badeball/cypress-cucumber-preprocessor`
- **Padrão de Projeto:** Page Object Model (POM)
- **CI/CD:** GitHub Actions
- **Relatórios:** `multiple-cucumber-html-reporter` (Relatório BDD em HTML)
- **Gerenciamento de Dados:** Cypress Fixtures (.json para dados de teste, .jpg para uploads)
- **Seletores e Interação Cypress:** Seletores CSS (`cy.get`, `cy.contains`), Comandos de Interação (`cy.click`, `cy.type`), Interceptação de Rede (`cy.intercept`, `cy.wait`), Asserções (`cy.should`), Manipulação de URL/Navegação (`cy.visit`, `cy.url`), Interação Cross-Origin (`cy.origin`)
- **Bundler/Pré-processador:** ESBuild (via `@bahmutov/cypress-esbuild-preprocessor`)
- **Gerenciador de Pacotes:** npm
- **Controle de Versão:** Git / GitHub

## 4. Estrutura do Projeto

O projeto segue uma estrutura organizada para facilitar a manutenção e escalabilidade:

/cypress
├── fixtures/ # Massa de dados (users.json, product_image.jpg, etc.)
├── integration/ # Arquivos de features BDD (.feature)
│ ├── admin/features # Features relacionadas ao painel admin
│ └── client/features # Features relacionadas à loja do cliente
├── pages/ # Page Objects (LoginPage.js, ProductsPage.js, etc.) - POM Unificado
├── support/
│ ├── commands.js # Comandos customizados do Cypress
│ ├── e2e.js # Arquivo de configuração principal do Cypress
│ └── step_definitions/ # Implementação dos steps Gherkin (common_steps.js, etc.) - Steps Unificados
├── utils/ # Funções auxiliares, gerenciadas separadamente para legibilidade e manutenibilidade
│
.github/
└── workflows/ # Arquivos de workflow do GitHub Actions
└──cypress-tests.yml
docs/
└──bugs/ #relatórios dos bugs encontrados
evidence/ #screenshots e vídeos comprovando o comportamento inesperado
generate-cucumber-report.js # Script Node.js para gerar o relatório HTML
cypress.config.js # Arquivo de configuração principal do Cypress
package.json # Dependências e scripts do projeto

## 5. Pré-requisitos

- [Node.js](https://nodejs.org/) (Versão 20.x ou superior recomendada)
- [npm](https://www.npmjs.com/) (geralmente instalado com o Node.js)
- [Git](https://git-scm.com/)

## 6. Instalação

1.  Clone o repositório:
    ```bash
    git clone https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
    cd SEU_REPOSITORIO
    ```
2.  Instale as dependências do projeto:
    ```bash
    npm ci
    ```
    _(Use `npm ci` para garantir a instalação exata das versões definidas no `package-lock.json`)_

## 7. Execução dos Testes

### 7.1. Execução Interativa (Cypress Test Runner)

Ideal para desenvolvimento e depuração:

```bash
npx cypress open
```

Selecione o navegador e o arquivo .feature que deseja executar.

### 7.2. Execução Headless (Linha de Comando)

Executa todos os testes definidos na configuração (ou via parâmetro --spec) em modo headless:

npx cypress run

Para executar um conjunto específico de features (ex: apenas testes de admin):

npx cypress run --spec "cypress/integration/admin/features/\*_/_.feature"

### 7.3. Geração do Relatório BDD HTML

Após a execução dos testes (via npx cypress run que gera os arquivos JSON do Cucumber), execute o script para gerar o relatório HTML:

node generate-cucumber-report.js

O relatório será gerado em reports/cucumber-html-report.html.

## 8. Integração Contínua (CI/CD) com GitHub Actions

Este projeto utiliza GitHub Actions para integração contínua. O workflow está configurado em .github/workflows/cypress-tests.yml e realiza as seguintes etapas:

Gatilhos: Executado em eventos de push e pull_request na branch main.

Ambiente: Configura um ambiente Ubuntu com Node.js v20.

Instalação: Instala as dependências usando npm ci (com cache para otimização).

Execução dos Testes:

Utiliza a action cypress-io/github-action@v6.

Importante: Por padrão, NÃO executa os testes E2E do fluxo de compra (purchase_flow.feature) e de gerenciamento de pedidos (manage_orders.feature) no pipeline de CI. Isso é feito intencionalmente para evitar a geração de dados persistentes (pedidos) na aplicação a cada execução do pipeline. A execução é limitada aos testes de authentication, authorization, login e manage_product via parâmetro spec:.

Geração do Relatório: Executa o script generate-cucumber-report.js.

Upload do Artefato: Disponibiliza o relatório HTML (cucumber-html-report.html) como um artefato do build no GitHub Actions.

(Link para o status do último build na badge no topo deste README)

## 9. Descobertas e Bugs Identificados

Durante o desenvolvimento da automação, foram identificadas as seguintes vulnerabilidades de segurança na aplicação WDE Shop:

BUG-AUTH-001: Falha de Autorização no Acesso a Páginas Administrativas

Descrição: Usuários autenticados com o perfil "cliente" conseguem acessar diretamente URLs de gerenciamento de produtos (/admin/products, /admin/products/edit/:id), que deveriam ser restritas a administradores.

Comprovação: Os testes automatizados em authorization.feature falham intencionalmente ao tentar acessar essas páginas como cliente, confirmando a vulnerabilidade.

Relatório Detalhado: (docs/bugs/BUG-AUTH-001.md)

BUG-AUTH-002: Falha de Autorização e Vazamento de Informação na Página de Pedidos

Descrição: Usuários autenticados como "cliente" conseguem acessar a URL /admin/orders. Embora a página apareça parcialmente quebrada (sem controles de admin), ela exibe informações de pedidos, incluindo pedidos de outros usuários (confirmado manualmente após execução do fluxo E2E que gera um pedido). Isso representa uma falha de autorização e um vazamento de informações (embora sem PII direta visível, os detalhes do pedido são expostos).

Comprovação: O teste automatizado em authorization.feature para /admin/orders não resulta em um redirecionamento esperado (401/403), e a verificação manual confirmou o acesso indevido a dados de outros usuários.

Relatório Detalhado: (docs/bugs/BUG-AUTH-002.md)

## 10. Desafios e Decisões Chave

Automação de Pagamento Externo (Stripe):

Desafio: O Cypress encontrou erros de cross-origin ao ser redirecionado para checkout.stripe.com. A tentativa de usar cy.origin() permitiu a validação do redirecionamento, mas a interação com elementos dentro da página do Stripe (provavelmente em iframes e com medidas anti-automação) provou-se extremamente complexa e instável.

Decisão: Encurtar o teste E2E purchase_flow.feature. O teste agora valida com sucesso o redirecionamento para o domínio do Stripe (cy.url().should('include', 'stripe.com')) usando cy.origin(), mas não prossegue com o preenchimento dos dados de pagamento.

Investigação do BUG-AUTH-002: O teste E2E, mesmo encurtado, foi útil para gerar dados (um pedido para o cliente) que permitiram a confirmação manual do vazamento de informações na página /admin/orders.

Otimização CI/CD: A utilização da action cypress-io/github-action com cache e a exclusão estratégica de testes que geram dados persistentes (purchase_flow.feature, manage_orders.feature) do fluxo padrão de CI garantem um feedback mais rápido e um ambiente de teste mais limpo.

Estrutura de Código: Decidiu-se por unificar os Page Objects (/pages) e Step Definitions (/support/step_definitions) para simplificar a estrutura, mantendo a separação lógica apenas nos arquivos .feature (/integration/admin e /integration/client).

Refatorações: Centralização da lógica de login em common_steps.js usando Background e steps parametrizados (Dado que eu estou logado como {string}) para reutilização em testes de admin e cliente.

## 11. Próximos Passos (Sugestões)

Embora o escopo definido para este projeto de portfólio tenha sido concluído, possíveis melhorias futuras poderiam incluir:

Implementação de um Linter (como ESLint) para padronização de código.

Expansão da cobertura de testes (mais cenários negativos, testes de API).

Integração com ferramentas de gerenciamento de testes (ex: TestRail, Zephyr Scale).

Exploração de testes visuais com ferramentas como Applitools ou Percy.
