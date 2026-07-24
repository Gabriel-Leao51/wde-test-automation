# BUG-SEC-005: Segredo de Sessão (`session secret`) Hardcoded no Código-Fonte

## Severidade

**MÉDIA**

- **Justificativa:** O segredo usado para assinar os cookies de sessão (`express-session`) está escrito literalmente no código-fonte (`config/session.js`), versionado no repositório Git. Qualquer pessoa com acesso ao código — incluindo o histórico do repositório, mesmo que o valor seja trocado depois — tem tudo o que precisa para **forjar cookies de sessão válidos**, potencialmente se autenticando como qualquer usuário sem precisar de credenciais.

## Prioridade

**MÉDIA**

- **Justificativa:** Não é explorável remotamente por um atacante sem acesso ao código-fonte, mas viola um princípio básico de gestão de segredos e representa risco real caso o repositório seja (ou se torne) público, ou em caso de vazamento de código-fonte.

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

2. O valor `"super-secret"` é o segredo usado pelo `express-session` (via `cookie-signature`) para assinar o cookie `connect.sid`. Qualquer um com esse valor pode gerar uma assinatura válida para um `sessionID` arbitrário (por exemplo, o `_id` de um usuário administrador conhecido) e apresentá-la ao servidor como se fosse uma sessão legítima.

## Resultado Esperado

O segredo de sessão deve vir de uma variável de ambiente (ex: `process.env.SESSION_SECRET`), gerada de forma aleatória e nunca commitada no controle de versão — seguindo o mesmo padrão já usado para `MONGODB_URI` e `STRIPE_KEY` neste projeto.

## Resultado Atual (Falha)

O segredo é uma string literal fixa no código-fonte, idêntica em toda instância da aplicação e visível a qualquer pessoa com acesso ao repositório (incluindo todo o histórico de commits, mesmo que seja alterado em um commit futuro).

## Evidências

- **Código-fonte:** `wde/config/session.js`, linha do campo `secret`.
- Não há um teste automatizado de ponta a ponta para este item nesta suíte — a forma mais direta de comprovação seria forjar um cookie assinado com esse segredo (usando o mesmo algoritmo de `cookie-signature`) e verificar que o servidor o aceita como válido; deixado como próximo passo manual/futuro dado o escopo desta rodada.

## Análise de Causa Raiz

O valor foi provavelmente deixado como placeholder durante o desenvolvimento inicial e nunca migrado para configuração via ambiente, ao contrário dos demais segredos da aplicação (`MONGODB_URI`, `STRIPE_KEY`), que já são lidos de variáveis de ambiente desde a dockerização do projeto.

## Impacto Potencial

- Falsificação de cookies de sessão, permitindo personificar qualquer usuário (incluindo administradores) sem conhecer suas credenciais, caso o segredo seja exposto (ex: repositório se tornar público, vazamento de código).
- Mesmo com o segredo trocado futuramente, o valor atual permanece no histórico do Git indefinidamente, a menos que o histórico seja reescrito.

## Recomendações

1. Mover `secret` para uma variável de ambiente (`SESSION_SECRET`), seguindo o padrão de `.env`/`.env.example` já estabelecido no projeto.
2. Gerar um valor aleatório forte (ex: `openssl rand -base64 32`) para cada ambiente.
3. Adicionar ao `README.md` a instrução de definir `SESSION_SECRET` no `.env`.
