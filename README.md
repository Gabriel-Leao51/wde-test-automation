# Automação de Testes (Portfólio QA) - WDE Shop

![Status CI](https://github.com/Gabriel-Leao51/wde-test-automation/actions/workflows/playwright-tests.yml/badge.svg)

## 1. Introdução

Este repositório contém um projeto de automação de testes E2E (End-to-End) desenvolvido como parte de um portfólio de Quality Assurance (QA). O objetivo principal foi construir uma suíte de testes robusta utilizando tecnologias modernas e boas práticas de mercado, demonstrando habilidades em automação, BDD, CI/CD e identificação de bugs.

A aplicação alvo (AUT - Application Under Test) é a **WDE Shop** ([repositório](https://github.com/Gabriel-Leao51/wde)), rodando localmente via Docker Compose (app + MongoDB), substituindo o deploy anteriormente hospedado no Render.

> Este projeto começou como uma suíte em **Cypress + Cucumber (JavaScript)** e foi migrado para **Playwright + pytest-bdd (Python)**. A suíte original em Cypress permanece preservada e consultável na branch [`legacy-cypress`](https://github.com/Gabriel-Leao51/wde-test-automation/tree/legacy-cypress). Detalhes da migração (decisões, fases, mapeamento Cypress → Playwright) estão em [ROADMAP.md](ROADMAP.md).

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
  - **Jornada de Compra:** Login do cliente, busca de produto, adição ao carrinho, checkout e redirecionamento completo até a página de pagamento (Stripe).

## 3. Tecnologias e Metodologias Utilizadas

- **Framework de Automação:** [Playwright](https://playwright.dev/python/) (Python, API síncrona)
- **Linguagem:** Python 3.12
- **Abordagem BDD:** Gherkin (PT-BR) via [pytest-bdd](https://pytest-bdd.readthedocs.io/)
- **Padrão de Projeto:** Page Object Model (POM)
- **Gerenciador de Pacotes:** [uv](https://docs.astral.sh/uv/)
- **CI/CD:** GitHub Actions
- **Relatórios:** `pytest-html` (relatório HTML autocontido), trace/vídeo/screenshot do Playwright retidos em falhas
- **Gerenciamento de Dados:** Fixtures JSON (`test_data/`) para usuários e pedidos, imagem de teste para upload
- **Aplicação alvo local:** Docker Compose ([repositório `wde`](https://github.com/Gabriel-Leao51/wde)) — app + MongoDB, com seed automático de dados
- **Controle de Versão:** Git / GitHub

## 4. Estrutura do Projeto

```
.
├── pyproject.toml              # Dependências e configuração do pytest (uv)
├── uv.lock
├── conftest.py                 # base_url, fixtures de Page Objects e login
├── features/
│   ├── admin/                  # Features de login, autenticação, autorização, produtos, pedidos
│   └── client/                 # Feature do fluxo de compra
├── steps/                      # Step definitions (pytest-bdd) + conftest.py com steps compartilhados
├── pages/                      # Page Objects (LoginPage, ProductsPage, CartPage, OrdersPage)
├── test_data/                  # Fixtures de dados (users.json, orders.json, mousepad.jpg)
├── utils/                      # Funções auxiliares (helpers.py)
├── docs/bugs/                  # Relatórios dos bugs encontrados
├── evidence/                   # Screenshots e vídeos comprovando o comportamento inesperado
├── .github/workflows/
│   └── playwright-tests.yml
└── ROADMAP.md                  # Roadmap e histórico da migração Cypress → Playwright
```

## 5. Pré-requisitos

- [Python](https://www.python.org/) 3.12+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (para rodar a aplicação alvo localmente)
- [Git](https://git-scm.com/)

## 6. Instalação

1. Clone os dois repositórios (a aplicação alvo e a suíte de testes):

   ```bash
   git clone https://github.com/Gabriel-Leao51/wde.git
   git clone https://github.com/Gabriel-Leao51/wde-test-automation.git
   ```

2. Suba a aplicação WDE Shop localmente (veja o [README do repositório `wde`](https://github.com/Gabriel-Leao51/wde#-rodando-localmente-com-docker) para detalhes — resumindo: `cp .env.example .env`, preencher `STRIPE_KEY`, e `docker compose up --build`). A aplicação sobe em `http://localhost:3000`, já com dados de teste populados pelo seed.

3. Instale as dependências da suíte de testes:

   ```bash
   cd wde-test-automation
   uv sync
   uv run playwright install --with-deps chromium
   ```

## 7. Execução dos Testes

### 7.1. Suíte completa

```bash
uv run pytest
```

### 7.2. Modo headed (com navegador visível)

```bash
uv run pytest --headed
```

Adicione `--slowmo=400` (valor em ms) para desacelerar as ações e facilitar a observação visual.

### 7.3. Um arquivo específico

```bash
uv run pytest steps/test_manage_product_steps.py
```

### 7.4. Execução paralela

```bash
uv run pytest -n 4
```

Usa [`pytest-xdist`](https://pytest-xdist.readthedocs.io/). Os 3 primeiros cenários de `manage_product.feature` (adicionar, editar, excluir) são interdependentes — operam sobre o mesmo produto em sequência — então carregam a tag `@xdist_group_product_crud`, que os fixa no mesmo worker (via `--dist=loadgroup`, já configurado em `pyproject.toml`, e o hook `pytest_bdd_apply_tag` em `conftest.py`). O 4º cenário (validação de campo obrigatório) é independente e não precisa da tag. O resto da suíte paraleliza livremente entre os demais workers.

`-n 4` é um teto deliberado, não `-n auto`: a WDE Shop roda como um único processo Node/Express + uma única instância MongoDB, sem escalonamento. Em testes locais, `-n auto` (usando todos os cores da máquina) gerou falhas intermitentes por timeout sob carga — o app simplesmente não responde rápido o suficiente com muitas sessões simultâneas. `-n 4` rodou de forma consistente em múltiplas execuções.

### 7.6. Apontando para outro ambiente

Por padrão a suíte aponta para `http://localhost:3000`. Para rodar contra outra URL:

```bash
WDE_BASE_URL=http://outro-host:3000 uv run pytest
```

### 7.7. Relatórios e artefatos de falha

Cada execução gera um relatório HTML autocontido em `playwright-report/report.html`. Falhas retêm automaticamente trace, vídeo e screenshot em `test-results/`, recuperáveis para depuração local:

```bash
uv run playwright show-trace test-results/<pasta-do-teste>/trace.zip
```

## 8. Integração Contínua (CI/CD) com GitHub Actions

O workflow está configurado em `.github/workflows/playwright-tests.yml` e realiza as seguintes etapas:

- **Gatilhos:** Executado em eventos de `push` e `pull_request` na branch `main`.
- **Ambiente:** Ubuntu com Python 3.12 (via `uv`) e Docker.
- **Aplicação alvo:** Faz checkout do repositório `wde` como um diretório irmão e sobe a stack via `docker compose up -d --build`, aguardando o health check antes de prosseguir.
- **Instalação:** `uv sync` + `playwright install --with-deps chromium`.
- **Execução dos Testes:** Roda o subconjunto principal (`login`, `authentication`, `authorization`, `manage_product`) em paralelo com `-n 4` (ver seção 7.4). Assim como na versão original em Cypress, os testes de `manage_orders.feature` e `purchase_flow.feature` ficam de fora do pipeline padrão — ambos geram pedidos persistentes no banco a cada execução, o que não é desejável em um pipeline de CI.
- **Bugs conhecidos como `@xfail`:** Os 3 cenários de `authorization.feature` que documentam `BUG-AUTH-001`/`BUG-AUTH-002` são marcados com a tag `@xfail` (com `xfail_strict` habilitado). Isso permite que o pipeline reporte sucesso normalmente enquanto continua executando e rastreando esses cenários — se algum dos bugs for corrigido, o cenário correspondente passa a `XPASS` e quebra o build, sinalizando a regressão em vez de passar despercebida.
- **Upload do Artefato:** Disponibiliza o relatório HTML e os artefatos de falha (`playwright-report/`, `test-results/`) como artefato do build no GitHub Actions.

(Link para o status do último build na badge no topo deste README.)

## 9. Descobertas e Bugs Identificados

Durante o desenvolvimento da automação, foram identificadas as seguintes vulnerabilidades de segurança na aplicação WDE Shop — ambas continuam presentes e são reproduzidas pela suíte atual (marcadas `@xfail` para não quebrar o CI, mas ainda executadas a cada run):

**BUG-AUTH-001: Falha de Autorização no Acesso a Páginas Administrativas**

Descrição: Usuários autenticados com o perfil "cliente" conseguem acessar diretamente URLs de gerenciamento de produtos (`/admin/products`, `/admin/products/:id`), que deveriam ser restritas a administradores.

Comprovação: Os cenários automatizados em `authorization.feature` documentam o comportamento esperado (acesso negado) e falham intencionalmente contra o comportamento real, confirmando a vulnerabilidade.

Relatório Detalhado: [BUG-AUTH-001 Report](docs/bugs/BUG-AUTH-001.md)

**BUG-AUTH-002: Falha de Autorização e Vazamento de Informação na Página de Pedidos**

Descrição: Usuários autenticados como "cliente" conseguem acessar a URL `/admin/orders`. Embora a página apareça parcialmente quebrada (sem controles de admin), ela exibe informações de pedidos, incluindo pedidos de outros usuários.

Comprovação: O cenário automatizado para `/admin/orders` não resulta na mensagem de autorização esperada, e a verificação manual confirmou o acesso indevido a dados de outros usuários.

Relatório Detalhado: [BUG-AUTH-002 Report](docs/bugs/BUG-AUTH-002.md)

## 10. Desafios e Decisões Chave

**Migração de Cypress/Cucumber (JS) para Playwright/pytest-bdd (Python):** decisão documentada em detalhe no [ROADMAP.md](ROADMAP.md), incluindo o mapeamento passo a passo de cada padrão Cypress para seu equivalente em Playwright.

**Automação de Pagamento Externo (Stripe) — limitação superada:** a versão em Cypress precisava de `cy.origin()` para validar apenas o redirecionamento para `checkout.stripe.com`, sem conseguir interagir com a página em si (cross-origin/iframes eram instáveis). O Playwright não tem essa limitação — navegação cross-origin é nativa — então o cenário `purchase_flow.feature` hoje valida o fluxo completo até o redirecionamento real para o Stripe, usando uma chave de teste (`sk_test_...`) de verdade.

**Bug de confiabilidade encontrado na aplicação (fora do escopo original de segurança):** ao validar o fluxo de compra localmente, uma falha na criação da sessão do Stripe (ex: chave inválida) derrubava o processo Node inteiro (`unhandled promise rejection` sem tratamento), tirando a aplicação do ar para todos os usuários. Corrigido diretamente no repositório `wde` (try/catch ao redor da chamada ao Stripe).

**CI/CD com bugs conhecidos:** rodar `authorization.feature` (que documenta bugs reais) no pipeline padrão deixava o build sempre vermelho, mesmo quando nada estava quebrado. A solução foi marcar os cenários como `@xfail` com `xfail_strict = true`, preservando a cobertura e a intenção original (falhar é o comportamento esperado) sem mascarar regressões de verdade.

**Estrutura de Código:** manteve-se a mesma filosofia da versão em Cypress — Page Objects unificados (`pages/`) e Step Definitions organizadas por feature (`steps/`), com steps compartilhados (como o login parametrizado por papel) centralizados em `steps/conftest.py`.

## 11. Próximos Passos (Sugestões)

Veja a seção "Fase 9" do [ROADMAP.md](ROADMAP.md) para a lista completa de melhorias habilitadas pela migração para Playwright, incluindo:

- Matriz multi-browser (Chromium/Firefox/WebKit) no CI.
- Execução paralela via `pytest-xdist`.
- Completar o checkout de teste do Stripe (preenchendo o cartão de teste), já que o Playwright lida melhor com iframes cross-origin.
- Testes de regressão visual com `expect(page).to_have_screenshot()`.
- Cobertura de API leve com `playwright.request`.
