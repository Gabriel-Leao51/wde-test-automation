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
  - **Jornada de Compra:** Login do cliente, busca de produto, adição ao carrinho, checkout, preenchimento do cartão de teste na página do Stripe e confirmação até a página de sucesso do pedido.
- **Regressão Visual:**
  - Comparação de screenshot vs. baseline aprovada em 5 páginas-chave: login, catálogo de produtos, detalhes de produto, painel administrativo de produtos e página de erro 401.

## 3. Tecnologias e Metodologias Utilizadas

- **Framework de Automação:** [Playwright](https://playwright.dev/python/) (Python, API síncrona)
- **Linguagem:** Python 3.12
- **Abordagem BDD:** Gherkin (PT-BR) via [pytest-bdd](https://pytest-bdd.readthedocs.io/)
- **Padrão de Projeto:** Page Object Model (POM)
- **Gerenciador de Pacotes:** [uv](https://docs.astral.sh/uv/)
- **CI/CD:** GitHub Actions
- **Relatórios:** `pytest-html` (relatório HTML autocontido), trace/vídeo/screenshot do Playwright retidos em falhas
- **Regressão Visual:** [`pytest-playwright-visual-snapshot`](https://pypi.org/project/pytest-playwright-visual-snapshot/) (equivalente Python ao `to_have_screenshot()`, que só existe no test runner JS/TS)
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
│   ├── client/                 # Feature do fluxo de compra
│   ├── security/                # Features de segurança avançada (hardening)
│   └── visual/                  # Feature de regressão visual
├── steps/                      # Step definitions (pytest-bdd) + conftest.py com steps compartilhados
├── pages/                      # Page Objects (LoginPage, ProductsPage, CartPage, OrdersPage, StripeCheckoutPage)
├── __snapshots__/              # Baselines de regressão visual (geradas em Linux — ver seção 7.9)
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

Por padrão roda em Chromium. Para rodar em outro navegador:

```bash
uv run pytest --browser=firefox
uv run pytest --browser=webkit
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

### 7.8. Suíte de segurança avançada (`features/security/`)

Além dos testes via UI/HTTP (Playwright), o cenário de prova de conceito do `BUG-SEC-005` conecta diretamente ao MongoDB para forjar uma sessão (ver relatório do bug para detalhes). Por isso, o `docker-compose.yml` do repositório `wde` publica a porta do MongoDB em `127.0.0.1:27017`. Se estiver rodando os testes fora do padrão local (`localhost:3000` + `localhost:27017`), aponte também a variável `MONGODB_URI`:

```bash
MONGODB_URI=mongodb://outro-host:27017 uv run pytest steps/test_security_hardening_steps.py
```

### 7.9. Regressão visual (`features/visual/`)

As baselines em `__snapshots__/` foram geradas em **Linux** (a mesma base Ubuntu Noble do runner `ubuntu-latest` do CI), porque o `pytest-playwright-visual-snapshot` grava o nome do arquivo com um valor fixo (não embutimos `sys.platform`, de propósito — ver ROADMAP, Fase 9). Renderização de fonte/anti-aliasing difere entre Windows e Linux, então rodar esses testes localmente no Windows sempre acusaria diferença, mesmo sem nenhuma mudança real de layout. Por isso:

- **Por padrão, ficam fora da suíte local:** `addopts` já inclui `-m "not visual"`, então `uv run pytest` (seção 7.1) não os executa.
- **No CI**, rodam explicitamente via `-m visual`, só no Chromium (para não triplicar a manutenção de baseline pela matriz).
- **Para rodar ou atualizar as baselines**, use a imagem oficial do Playwright (mesma base do CI), conectada à rede Docker da aplicação:

  ```bash
  docker run --rm --network wde_default \
    -v "$(pwd):/work" -w /work \
    -e WDE_BASE_URL=http://wde-app-1:3000 \
    mcr.microsoft.com/playwright/python:v1.61.0-noble \
    bash -c "pip install --quiet pymongo pytest pytest-bdd pytest-html pytest-playwright pytest-xdist pytest-playwright-visual-snapshot && python -m pytest -m visual --browser chromium --update-snapshots steps/test_visual_regression_steps.py"
  ```

  Use `wde-app-1` (nome do container, não `app`) como host: o Chromium força HTTPS em qualquer host chamado literalmente `app` via HSTS preload do gTLD `.app`, o que quebra `http://app:3000`. Sem `--update-snapshots`, o mesmo comando compara contra a baseline existente.

## 8. Integração Contínua (CI/CD) com GitHub Actions

O workflow está configurado em `.github/workflows/playwright-tests.yml` e realiza as seguintes etapas:

- **Gatilhos:** Executado em eventos de `push` e `pull_request` na branch `main`.
- **Ambiente:** Ubuntu com Python 3.12 (via `uv`) e Docker.
- **Aplicação alvo:** Faz checkout do repositório `wde` como um diretório irmão e sobe a stack via `docker compose up -d --build`, aguardando o health check antes de prosseguir.
- **Matriz multi-browser:** roda o job completo 3 vezes em paralelo (Chromium, Firefox, WebKit), cada um com sua própria stack Docker isolada (evita interferência de concorrência entre browsers). `fail-fast: false` — a falha em um navegador não cancela os outros.
- **Instalação:** `uv sync` + `playwright install --with-deps <browser-da-matriz>`.
- **Execução dos Testes:** Roda o subconjunto principal (`login`, `authentication`, `authorization`, `manage_product`) em paralelo via `pytest-xdist` (ver seção 7.4) — `-n 4` para Chromium, `-n 2` para Firefox/WebKit (processos mais pesados, tiveram timeouts intermitentes em `-n 4` durante validação local). Assim como na versão original em Cypress, os testes de `manage_orders.feature` e `purchase_flow.feature` ficam de fora do pipeline padrão — ambos geram pedidos persistentes no banco a cada execução, o que não é desejável em um pipeline de CI.
- **Regressão visual:** roda como um passo extra, só na perna Chromium da matriz (`-m visual`, ver seção 7.9), comparando contra as baselines Linux versionadas em `__snapshots__/`.
- **Bugs conhecidos como `@xfail`:** Os 3 cenários de `authorization.feature` que documentam `BUG-AUTH-001`/`BUG-AUTH-002` são marcados com a tag `@xfail` (com `xfail_strict` habilitado). Isso permite que o pipeline reporte sucesso normalmente enquanto continua executando e rastreando esses cenários — se algum dos bugs for corrigido, o cenário correspondente passa a `XPASS` e quebra o build, sinalizando a regressão em vez de passar despercebida.
- **Upload do Artefato:** Disponibiliza o relatório HTML e os artefatos de falha (`playwright-report/`, `test-results/`) como artefato do build no GitHub Actions.

(Link para o status do último build na badge no topo deste README.)

## 9. Descobertas e Bugs Identificados

Durante o desenvolvimento da automação, foram identificadas vulnerabilidades de segurança na aplicação WDE Shop. As que seguem presentes são reproduzidas pela suíte atual (marcadas `@xfail` para não quebrar o CI, mas ainda executadas a cada run em `features/security/hardening.feature` e `features/admin/authorization.feature`).

### Corrigidos

**NoSQL Injection → Crash Total da Aplicação (não autenticado)**

Descrição: `POST /login` (ou `/signup`) com corpo JSON `{"email":{"$ne":null},"password":{"$ne":null}}` fazia o MongoDB interpretar `$ne` como operador de consulta (contornando a busca por e-mail exato) e, em seguida, derrubava o processo Node inteiro ao passar um objeto (em vez de string) para `bcrypt.compare()` — uma exceção não tratada. Um único request não autenticado bastava para tirar a aplicação do ar para todos os usuários.

Correção: validação de tipo (`email`/`password` devem ser strings) adicionada em `controllers/auth.controller.js` e `util/validation.js`, fechando tanto o vetor de injeção quanto o crash.

Comprovação: `features/security/hardening.feature`, cenários de NoSQL injection em `/login` e `/signup` — hoje passam normalmente (não são mais `@xfail`), validando que a aplicação responde com "Invalid credentials" e permanece no ar.

### Ainda presentes

**BUG-AUTH-001: Falha de Autorização no Acesso a Páginas Administrativas**

Descrição: Usuários autenticados com o perfil "cliente" conseguem acessar diretamente URLs de gerenciamento de produtos (`/admin/products`, `/admin/products/:id`), que deveriam ser restritas a administradores.

Comprovação: Os cenários automatizados em `authorization.feature` documentam o comportamento esperado (acesso negado) e falham intencionalmente contra o comportamento real, confirmando a vulnerabilidade.

Relatório Detalhado: [BUG-AUTH-001 Report](docs/bugs/BUG-AUTH-001.md)

**BUG-AUTH-002: Falha de Autorização e Vazamento de Informação na Página de Pedidos**

Descrição: Usuários autenticados como "cliente" conseguem acessar a URL `/admin/orders`. Embora a página apareça parcialmente quebrada (sem controles de admin), ela exibe informações de pedidos, incluindo pedidos de outros usuários.

Comprovação: O cenário automatizado para `/admin/orders` não resulta na mensagem de autorização esperada, e a verificação manual confirmou o acesso indevido a dados de outros usuários.

Relatório Detalhado: [BUG-AUTH-002 Report](docs/bugs/BUG-AUTH-002.md)

**BUG-INFO-001: Exposição de Detalhes Internos do Servidor em Páginas de Erro**

Descrição: `NODE_ENV` nunca é definido como `production`, então qualquer exceção não tratada expõe caminhos do servidor, trechos de código-fonte dos templates e stack traces do Node ao cliente. Agravado por uma falha em cascata: a própria página de erro (`500.ejs`) quebra ao tentar renderizar `locals.cart`, que não existe em erros disparados antes do `cartMiddleware` rodar (ex: rejeição de CSRF).

Relatório Detalhado: [BUG-INFO-001 Report](docs/bugs/BUG-INFO-001.md)

**BUG-SEC-002: Ausência de Headers HTTP de Segurança**

Descrição: Nenhum header de segurança padrão (`Content-Security-Policy`, `X-Frame-Options`, `X-Content-Type-Options`, etc.) está presente nas respostas, e `X-Powered-By: Express` vaza a stack tecnológica. Nenhum middleware de segurança (`helmet` ou equivalente) está em uso.

Relatório Detalhado: [BUG-SEC-002 Report](docs/bugs/BUG-SEC-002.md)

**BUG-SEC-003: Token CSRF Exposto na URL do Formulário de Produto**

Descrição: O formulário de produto envia o token CSRF como parâmetro de query string (`?_csrf=...`) na `action`, em vez de campo oculto — diferente de todos os outros formulários da aplicação, que fazem isso corretamente.

Relatório Detalhado: [BUG-SEC-003 Report](docs/bugs/BUG-SEC-003.md)

**BUG-SEC-004: Cookie de Sessão sem Flags `Secure`/`SameSite`**

Descrição: O cookie `connect.sid` define apenas `HttpOnly`; `Secure` e `SameSite` não são configurados explicitamente.

Relatório Detalhado: [BUG-SEC-004 Report](docs/bugs/BUG-SEC-004.md)

**BUG-SEC-005: Segredo de Sessão Hardcoded → Personificação Completa de Administrador (CRÍTICA)**

Descrição: `config/session.js` usa a string literal `"super-secret"` como segredo de assinatura de sessão, em vez de uma variável de ambiente. Comprovado via prova de conceito funcional: um cookie de sessão forjado do zero (assinado com esse segredo, sem nunca chamar `/login`) é aceito pelo servidor e concede acesso administrativo completo.

Comprovação: `features/security/hardening.feature`, cenário "Um cookie de sessão forjado com o segredo hardcoded não deve conceder acesso" — insere uma sessão diretamente no MongoDB, assina o cookie com o mesmo algoritmo do `cookie-signature`, e confirma que `GET /admin/products` retorna o painel administrativo completo usando apenas esse cookie.

Relatório Detalhado: [BUG-SEC-005 Report](docs/bugs/BUG-SEC-005.md)

## 10. Desafios e Decisões Chave

**Migração de Cypress/Cucumber (JS) para Playwright/pytest-bdd (Python):** decisão documentada em detalhe no [ROADMAP.md](ROADMAP.md), incluindo o mapeamento passo a passo de cada padrão Cypress para seu equivalente em Playwright.

**Automação de Pagamento Externo (Stripe) — checkout completo:** a versão em Cypress precisava de `cy.origin()` para validar apenas o redirecionamento para `checkout.stripe.com`, sem conseguir interagir com a página em si (cross-origin/iframes eram instáveis). O Playwright não tem essa limitação — navegação cross-origin é nativa — e, na prática, os campos de cartão da página hospedada do Stripe renderizam diretamente no documento principal (não num iframe cross-origin), o que tornou a automação direta. O cenário `purchase_flow.feature` hoje completa o fluxo real: preenche o cartão de teste (`4242 4242 4242 4242`) usando uma chave de teste (`sk_test_...`) de verdade, confirma o pagamento e valida o redirecionamento até `/orders/success`. Testado e confiável nos 3 navegadores da matriz (Chromium, Firefox, WebKit) — o hCaptcha presente na página não bloqueou a automação em nenhum deles.

**Bug de confiabilidade encontrado na aplicação (fora do escopo original de segurança):** ao validar o fluxo de compra localmente, uma falha na criação da sessão do Stripe (ex: chave inválida) derrubava o processo Node inteiro (`unhandled promise rejection` sem tratamento), tirando a aplicação do ar para todos os usuários. Corrigido diretamente no repositório `wde` (try/catch ao redor da chamada ao Stripe).

**CI/CD com bugs conhecidos:** rodar `authorization.feature` (que documenta bugs reais) no pipeline padrão deixava o build sempre vermelho, mesmo quando nada estava quebrado. A solução foi marcar os cenários como `@xfail` com `xfail_strict = true`, preservando a cobertura e a intenção original (falhar é o comportamento esperado) sem mascarar regressões de verdade.

**Estrutura de Código:** manteve-se a mesma filosofia da versão em Cypress — Page Objects unificados (`pages/`) e Step Definitions organizadas por feature (`steps/`), com steps compartilhados (como o login parametrizado por papel) centralizados em `steps/conftest.py`.

**Regressão visual — outro gap Python vs. JS/TS do Playwright:** assim como o "UI mode" (`--ui`), `expect(page).to_have_screenshot()` só existe no test runner JS/TS — confirmado por busca exaustiva na API Python instalada (`playwright/_impl/_assertions.py`, `playwright/sync_api/_generated.py`). O equivalente adotado foi o pacote de terceiros `pytest-playwright-visual-snapshot`. Como ele embute o nome da plataforma no arquivo de snapshot, gerar as baselines no Windows as tornaria inúteis para o CI (`ubuntu-latest`); a solução foi gerá-las dentro da própria imagem Docker oficial do Playwright, conectada à rede do `docker-compose.yml` da aplicação (ver seção 7.9). Isso também expôs um efeito colateral do Chromium: o nome de serviço `app` do Compose colide com a HSTS-preload do gTLD `.app`, forçando HTTPS e quebrando a conexão HTTP simples — contornado usando o nome do container (`wde-app-1`) em vez do nome do serviço.

## 11. Próximos Passos (Sugestões)

Veja a seção "Fase 9" do [ROADMAP.md](ROADMAP.md) para a lista completa de melhorias habilitadas pela migração para Playwright. Todos os itens já concluídos: matriz multi-browser (Chromium/Firefox/WebKit) no CI, execução paralela via `pytest-xdist`, checkout de teste do Stripe completo, cobertura leve de API via `playwright.request` (usada nos testes de segurança) e regressão visual (`features/visual/`, seção 7.9).
