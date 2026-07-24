# BUG-SEC-005: Segredo de Sessão (`session secret`) Hardcoded no Código-Fonte

## Severidade

**CRÍTICA**

- **Justificativa:** Comprovado por prova de conceito automatizada (ver Evidências): conhecer o valor `"super-secret"` é suficiente para forjar um cookie `connect.sid` assinado corretamente e obter acesso administrativo completo (`/admin/products` renderizado com sucesso) **sem nunca chamar `/login` e sem conhecer nenhuma credencial**. Não é "potencialmente" explorável — é personificação de administrador de ponta a ponta, comprovada nesta rodada.

## Prioridade

**ALTA**

- **Justificativa:** Não é explorável remotamente por um atacante sem acesso ao segredo (que hoje só está no código-fonte), mas uma vez obtido o segredo, o impacto é total e imediato — sem necessidade de senha, token de sessão roubado ou qualquer outra credencial. Risco real caso o repositório seja (ou se torne) público, ou em caso de vazamento de código-fonte.

## Ambiente

- **Aplicação:** WDE Shop
- **Arquivo:** `config/session.js`

## Detalhes do Relato

- **Relatado por:** Gabriel Leão (com assistência de Claude)
- **Data da Descoberta:** 24/07/2026

## Passos para Reproduzir

1. Inspecionar `config/session.js` no repositório:

   ```js
   function createSessionConfig() {
     return {
       secret: "super-secret",
       resave: false,
       saveUninitialized: false,
       store: createSessionStore(),
       cookie: {
         maxAge: 2 * 24 * 60 * 60 * 1000,
       },
     };
   }
   ```

2. O valor `"super-secret"` é o segredo usado pelo `express-session` (via `cookie-signature`) para assinar o cookie `connect.sid`. Qualquer um com esse valor pode gerar uma assinatura válida para um `sessionID` arbitrário e apresentá-la ao servidor como se fosse uma sessão legítima.

3. **Prova de conceito completa** (reproduzida em `steps/test_security_hardening_steps.py`, função `forge_admin_session_cookie` + cenário "Um cookie de sessão forjado com o segredo hardcoded não deve conceder acesso" em `features/security/hardening.feature`):

   a. Conectar diretamente ao MongoDB (`sessions` collection, mesmo schema usado pelo `connect-mongodb-session`) e inserir um documento de sessão arbitrário, com `uid` apontando para o `_id` real de um usuário administrador e `isAdmin: true` — sem nunca ter feito login:

      ```python
      db.sessions.insert_one({
          "_id": forged_sid,
          "session": {"cookie": {...}, "uid": str(admin_user["_id"]), "isAdmin": True},
          "expires": expires_at,
      })
      ```

   b. Assinar o `sid` escolhido com o mesmo algoritmo do `cookie-signature` (`HMAC-SHA256` em base64, sem padding), usando o segredo hardcoded:

      ```python
      mac = hmac.new(b"super-secret", forged_sid.encode(), hashlib.sha256).digest()
      cookie_value = f"s:{forged_sid}." + base64.b64encode(mac).decode().rstrip("=")
      ```

   c. Fazer uma requisição `GET /admin/products` usando **apenas** esse cookie forjado, em um contexto de requisição totalmente novo e isolado (sem nenhum cookie de uma sessão real).

## Resultado Esperado

O segredo de sessão deve vir de uma variável de ambiente (ex: `process.env.SESSION_SECRET`), gerada de forma aleatória e nunca commitada no controle de versão — seguindo o mesmo padrão já usado para `MONGODB_URI` e `STRIPE_KEY` neste projeto. Um cookie forjado dessa forma não deveria ser aceito pelo servidor.

## Resultado Atual (Falha)

- O segredo é uma string literal fixa no código-fonte, idêntica em toda instância da aplicação e visível a qualquer pessoa com acesso ao repositório (incluindo todo o histórico de commits, mesmo que seja alterado em um commit futuro).
- **Confirmado por execução real:** a requisição `GET /admin/products` com o cookie forjado retornou `200 OK` com o HTML completo do painel administrativo (`Manage Products` presente na resposta) — acesso de administrador obtido sem nunca chamar `/login`.

## Evidências

- **Código-fonte:** `wde/config/session.js`, linha do campo `secret`.
- **Teste Automatizado (prova de conceito funcional):** `features/security/hardening.feature`, cenário "Um cookie de sessão forjado com o segredo hardcoded não deve conceder acesso" (`@xfail`, tag `@session`) — forja um cookie do zero (sem depender de nenhuma sessão pré-existente) e comprova que o servidor concede acesso administrativo com base apenas nele.

## Análise de Causa Raiz

O valor foi provavelmente deixado como placeholder durante o desenvolvimento inicial e nunca migrado para configuração via ambiente, ao contrário dos demais segredos da aplicação (`MONGODB_URI`, `STRIPE_KEY`), que já são lidos de variáveis de ambiente desde a dockerização do projeto.

## Impacto Potencial (Confirmado)

- **Personificação completa de qualquer usuário, incluindo administradores, sem conhecer nenhuma credencial** — demonstrado nesta rodada via prova de conceito funcional, condicionado apenas ao segredo estar exposto (ex: repositório se tornar público, vazamento de código).
- Mesmo com o segredo trocado futuramente, o valor atual permanece no histórico do Git indefinidamente, a menos que o histórico seja reescrito.

## Recomendações

1. Mover `secret` para uma variável de ambiente (`SESSION_SECRET`), seguindo o padrão de `.env`/`.env.example` já estabelecido no projeto.
2. Gerar um valor aleatório forte (ex: `openssl rand -base64 32`) para cada ambiente.
3. Adicionar ao `README.md` a instrução de definir `SESSION_SECRET` no `.env`.
