# Roadmap: Migração Cypress + Cucumber (JS) → Playwright + pytest-bdd (Python)

## 1. Contexto

Este projeto (`wde_automacao`) contém uma suíte E2E em **Cypress + `@badeball/cypress-cucumber-preprocessor`**, testando a aplicação **WDE Shop** (`https://wde-5p3f.onrender.com`). Cobertura atual:

- **Admin:** login (happy/negative path), autenticação (401), autorização (403 / bugs conhecidos), CRUD de produtos, gerenciamento de pedidos.
- **Cliente:** fluxo de compra E2E (login → produto → carrinho → redirecionamento Stripe).
- **Achados de segurança documentados:** `BUG-AUTH-001` (bypass de autorização em `/admin/products`) e `BUG-AUTH-002` (vazamento de dados de pedidos em `/admin/orders`), com evidências em `evidence/`.

Decisões já tomadas para a migração:

| Decisão | Escolha |
|---|---|
| Linguagem | **Python** |
| BDD | Manter Gherkin (`.feature`), via **pytest-bdd** |
| Runner/Browser | **pytest-playwright** (Playwright oficial para Python) |
| Gerenciador de pacotes | **uv** |
| Modo de execução | Roadmap primeiro → implementação fase a fase |

Este é um projeto **novo por dentro** (troca de linguagem, não só de framework), mas mantém: os mesmos `.feature` em PT-BR, o mesmo Page Object Model, os mesmos dados de teste, e os mesmos relatórios de bugs/evidências — só a camada de execução muda.

## 2. Por que essa stack

- **pytest-bdd**: mapeia `.feature` para testes pytest via `@scenario`/`scenarios()`; ganha todo o ecossistema pytest (fixtures, `-n auto` com `pytest-xdist`, `pytest-html`, markers `@happy-path`/`@negative-path` como pytest marks).
- **pytest-playwright**: plugin oficial (`page`, `browser`, `context` fixtures prontas; `--browser`, `--headed`, `--tracing`, `--video` via CLI).
- **Simplificação real vs. Cypress**: o teste de checkout Stripe usava `cy.origin()` para contornar a limitação de cross-origin do Cypress e mesmo assim não conseguia interagir com o iframe do Stripe. Playwright **não tem essa limitação** — navegação cross-origin e iframes são nativos. Isso abre a possibilidade de, no futuro, completar o fluxo de pagamento de teste (ver Fase 9).

## 3. Estrutura de diretórios proposta

```
wde_automacao/
├── pyproject.toml              # uv + pytest + pytest-bdd + pytest-playwright
├── uv.lock
├── pytest.ini                  # ou [tool.pytest.ini_options] no pyproject
├── conftest.py                 # base_url, fixtures de login/role, paths de feature
├── features/
│   ├── admin/
│   │   ├── authentication.feature
│   │   ├── authorization.feature
│   │   ├── login.feature
│   │   └── manage_orders.feature
│   │   └── manage_product.feature
│   └── client/
│       └── purchase_flow.feature
├── steps/
│   ├── __init__.py
│   ├── test_admin_login_steps.py
│   ├── test_common_steps.py
│   ├── test_manage_orders_steps.py
│   ├── test_manage_product_steps.py
│   ├── test_purchase_flow_steps.py
│   └── test_security_steps.py
├── pages/
│   ├── __init__.py
│   ├── login_page.py
│   ├── products_page.py
│   ├── cart_page.py
│   └── orders_page.py
├── test_data/                  # equivalente a cypress/fixtures
│   ├── users.json
│   ├── orders.json
│   └── mousepad.jpg
├── utils/
│   └── helpers.py              # format_product_data()
├── docs/bugs/                  # mantido como está
├── evidence/                   # mantido como está
├── .github/workflows/
│   └── playwright-tests.yml
└── README.md                   # reescrito para a stack Python
```

`features/` fica separado de `steps/` (diferente do Cypress, que unificava tudo em `support/`) porque é o padrão idiomático do pytest-bdd e evita ambiguidade entre "step definition" e "test file" do pytest.

## 4. Mapeamento Cypress → Playwright/pytest-bdd

| Cypress | Playwright/Python | Observação |
|---|---|---|
| `cy.visit(path)` | `page.goto(path)` | `base_url` via `pytest-playwright` (`--base-url` ou fixture) |
| `cy.get(selector)` | `page.locator(selector)` | preferir `get_by_role`/`get_by_label`/`get_by_text` onde fizer sentido |
| `cy.contains(sel, text)` | `page.locator(sel).filter(has_text=text)` ou `get_by_text` | |
| `.type(text)` | `.fill(text)` | Playwright não precisa de `.clear()` antes — `fill` já substitui |
| `.selectFile(path)` | `.set_input_files(path)` | |
| `.should('be.visible')` | `expect(locator).to_be_visible()` | `playwright.sync_api.expect`, com auto-retry embutido |
| `cy.intercept()` + `cy.wait('@alias')` | `with page.expect_response(url_pattern) as resp_info:` | bloco `with` em volta da ação que dispara a request |
| `cy.origin('https://checkout.stripe.com', ...)` | nada especial — `page.wait_for_url("**checkout.stripe.com**")` | Playwright lida com cross-origin nativamente |
| `cy.fixture('users.json')` | `json.load(open("test_data/users.json"))` via fixture pytest | |
| Page Objects (classes JS, `export default new X()`) | classes Python recebendo `page: Page` no `__init__` | instanciadas via fixture pytest (`@pytest.fixture def login_page(page): return LoginPage(page)`) |
| `element.validity.valid` / `validationMessage` | `locator.evaluate("el => el.validity.valid")` | mesma abordagem, via `evaluate` |
| Tags Gherkin (`@crud @product @happy-path`) | marks pytest via `pytest-bdd` (`pytest.mark.crud` etc.) | permite `pytest -m happy_path` |
| `multiple-cucumber-html-reporter` | `pytest-html` (Fase 6) ou `allure-pytest-bdd` (stretch) | ver Fase 6 |
| `cypress-io/github-action` | `astral-sh/setup-uv` + `playwright install --with-deps` | ver Fase 7 |

## 5. Fases

### Fase 0 — Scaffolding do projeto
- [ ] `uv init`, `pyproject.toml` com Python ≥ 3.11
- [ ] Dependências: `pytest`, `pytest-bdd`, `pytest-playwright`, `playwright`
- [ ] `uv run playwright install --with-deps chromium`
- [ ] Estrutura de pastas (seção 3), `.gitignore` atualizado (`.venv/`, `__pycache__/`, `test-results/`, `playwright-report/`)
- [ ] `conftest.py` com fixture `base_url` (`https://wde-5p3f.onrender.com`)

**Pronto quando:** `uv run pytest --collect-only` roda sem erro (mesmo sem testes ainda).

### Fase 1 — Infraestrutura central (dados + Page Objects)
- [ ] Portar `users.json`, `orders.json`, `mousepad.jpg` → `test_data/`
- [ ] Portar `helpers.js` → `utils/helpers.py` (`format_product_data`)
- [ ] Page Objects Python: `LoginPage`, `ProductsPage`, `CartPage`, `OrdersPage`
- [ ] Fixture de login parametrizada por papel (`admin`/`cliente`), equivalente ao `commonSteps.js`

**Pronto quando:** Page Objects têm cobertura de smoke manual (script solto ou teste único de login).

### Fase 2 — Login e segurança (admin)
- [ ] `login.feature`, `authentication.feature`, `authorization.feature`
- [ ] `test_admin_login_steps.py`, `test_security_steps.py`, `test_common_steps.py`
- [ ] Confirmar que os 2 bugs conhecidos (`BUG-AUTH-001`, `BUG-AUTH-002`) ainda reproduzem igual (mesmos cenários "devem falhar")

**Pronto quando:** os cenários rodam contra o app publicado e o resultado (pass/fail) bate com o comportamento documentado nos relatórios de bug.

### Fase 3 — CRUD de produtos (admin)
- [ ] `manage_product.feature` + `test_manage_product_steps.py`
- [ ] `fillProductForm` → método Python no `ProductsPage` (mapa de campos igual ao original)
- [ ] Validação de campo obrigatório via `validity`/`validationMessage`

**Pronto quando:** os 4 cenários (add, edit, delete, validação) passam de ponta a ponta.

### Fase 4 — Gerenciamento de pedidos (admin)
- [ ] `manage_orders.feature` + `test_manage_orders_steps.py`
- [ ] Troca de `cy.intercept`/`cy.wait` por `page.expect_response`

**Pronto quando:** update de status reflete no badge, aguardando a resposta de rede real (não um `sleep`).

### Fase 5 — Fluxo de compra do cliente (E2E + Stripe)
- [ ] `purchase_flow.feature` + `test_purchase_flow_steps.py`
- [ ] Reproduzir o comportamento atual (parar na confirmação de redirecionamento ao domínio Stripe)
- [ ] Registrar como "stretch" (Fase 9) a possibilidade de ir além, já que Playwright lida melhor com iframes/cross-origin

**Pronto quando:** cenário passa e gera o mesmo pedido de teste que hoje permite validar `BUG-AUTH-002` manualmente.

### Fase 6 — Relatórios e artefatos de falha
- [ ] Escolher entre `pytest-html` (simples) ou `allure-pytest-bdd` (visual, mais próximo do Cucumber HTML atual) — sugestão: começar com `pytest-html`, migrar para Allure se quiser algo mais "portfolio-ready"
- [ ] Configurar `--tracing=retain-on-failure --video=retain-on-failure --screenshot=only-on-failure` (equivalente ao `video: true` do Cypress, mas só guarda em falha)

**Pronto quando:** uma falha proposital gera trace/vídeo/screenshot recuperável localmente.

### Fase 7 — CI/CD (GitHub Actions)
- [ ] Novo workflow `playwright-tests.yml`: setup Python + `uv`, `uv sync`, `playwright install --with-deps`
- [ ] Manter a mesma exclusão estratégica de CI (sem `purchase_flow` e `manage_orders` no pipeline padrão, mesmo motivo: evitar dados persistentes)
- [ ] Upload de artefatos (`playwright-report/`, `test-results/`)
- [ ] Atualizar badge no README

**Pronto quando:** PR de teste dispara o workflow e o artefato de relatório fica disponível no Actions.

### Fase 8 — Documentação e limpeza
- [ ] Reescrever `README.md` (stack, estrutura, instalação via `uv sync`, execução via `uv run pytest`)
- [ ] Manter `docs/bugs/` e `evidence/` (ainda válidos, só ajustar referências de comando se citarem Cypress)
- [ ] Antes de remover `cypress/`, `cypress.config.js`, `generate-cucumber-report.js`, `cucumber-messages.ndjson`: criar tag/branch `legacy-cypress` para preservar histórico consultável

**Pronto quando:** README reflete só a stack nova, e a suíte Cypress antiga está preservada em `legacy-cypress` mas fora do diretório principal.

### Fase 9 — Melhorias habilitadas pelo Playwright (stretch, pós-paridade)
- [ ] Matriz multi-browser (chromium/firefox/webkit) no CI — Cypress hoje só roda Chrome
- [ ] Execução paralela via `pytest-xdist`
- [ ] Tentar completar o checkout de teste do Stripe (cartão de teste `4242...`) já que Playwright lida melhor com iframes cross-origin
- [ ] Testes de regressão visual com `expect(page).to_have_screenshot()`
- [ ] Cobertura de API leve com `playwright.request` (ex.: validar respostas JSON de `/admin/orders/:id` diretamente)

## 6. Riscos / pontos de atenção

- **Mudança de linguagem = zero reaproveitamento de código**, só de estrutura/lógica. Cada step precisa ser reescrito, não só traduzido 1:1.
- **App alvo é um deploy gratuito no Render** (`wde-5p3f.onrender.com`) — pode hibernar/cold-start; considerar `timeout` maior no primeiro `goto` de cada sessão de CI.
- **`manage_orders.feature` depende de um `testOrderId` fixo** (`orders.json`) — se esse pedido for removido/alterado no banco do app, o cenário quebra independente da migração.
- **Bugs de autorização são o "produto" deste portfólio** — qualquer step de segurança precisa ser validado com atenção extra para não mascarar acidentalmente o bug real durante a reescrita.

## 7. Próximo passo imediato

Começar pela **Fase 0** (scaffolding) assim que este roadmap for aprovado.
