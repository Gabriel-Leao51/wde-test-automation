# BUG-SEC-002: Ausência de Headers HTTP de Segurança

## Severidade

**MÉDIA**

- **Justificativa:** Nenhum header de segurança padrão de mercado está presente nas respostas HTTP. Isoladamente cada ausência é de risco moderado, mas em conjunto deixam a aplicação sem defesas em profundidade contra clickjacking, MIME-sniffing, e reduzem a eficácia de outras mitigações (como CSP contra XSS). O header `X-Powered-By: Express` também facilita fingerprinting da stack tecnológica.

## Prioridade

**MÉDIA**

## Ambiente

- **Aplicação:** WDE Shop
- **URL Base:** `http://localhost:3000`
- **Endpoint Afetado:** todas as rotas (testado em `/products`, mas o comportamento é da configuração global do Express)

## Detalhes do Relato

- **Relatado por:** Gabriel Leão (com assistência de Claude)
- **Data da Descoberta:** 24/07/2026

## Passos para Reproduzir

```bash
curl -I http://localhost:3000/products
```

## Resultado Esperado

Presença de headers de segurança padrão, por exemplo:

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY` (ou `SAMEORIGIN`)
- `Content-Security-Policy: ...`
- `Referrer-Policy: ...`
- Ausência do header `X-Powered-By`

## Resultado Atual (Falha)

Resposta real capturada:

```
HTTP/1.1 200 OK
X-Powered-By: Express
Content-Type: text/html; charset=utf-8
Content-Length: 3164
ETag: W/"c5c-XiJXTqKGgMSMNLHHjVu1+4Q2hEE"
Set-Cookie: connect.sid=...; Path=/; Expires=...; HttpOnly
Date: ...
Connection: keep-alive
Keep-Alive: timeout=5
```

Nenhum header de segurança está presente, e `X-Powered-By: Express` revela a stack tecnológica.

## Evidências

- **Teste Automatizado:** `features/security/hardening.feature`, cenário "A aplicação deve responder com headers de segurança padrão" (`@xfail`, tag `@headers`).
- **Reprodução manual:** comando `curl -I` acima.

## Análise de Causa Raiz

Nenhum middleware de segurança (ex: [`helmet`](https://helmetjs.github.io/)) está registrado em `app.js`. Não há configuração manual de headers de segurança em nenhum ponto da aplicação.

## Impacto Potencial

- Sem `X-Frame-Options`/`frame-ancestors` (CSP), a aplicação pode ser embutida em um `<iframe>` de um site malicioso (clickjacking).
- Sem `X-Content-Type-Options: nosniff`, navegadores podem tentar adivinhar o tipo de conteúdo de respostas, abrindo espaço para ataques de MIME-sniffing.
- Sem CSP, não há camada de defesa adicional caso um vetor de XSS seja encontrado no futuro.
- `X-Powered-By: Express` facilita a um atacante identificar rapidamente a stack e buscar vulnerabilidades conhecidas específicas do framework/versão.

## Recomendações

1. Adicionar [`helmet`](https://www.npmjs.com/package/helmet) como dependência e registrá-lo no início da cadeia de middlewares em `app.js` — cobre a maioria destes itens (incluindo desabilitar `X-Powered-By`) com configuração mínima.
2. Configurar uma `Content-Security-Policy` adequada ao uso de scripts inline/estilos existentes na aplicação (o `helmet` permite customização por diretiva).
3. Revisar se `frame-ancestors`/`X-Frame-Options` deve ser `DENY` (nenhum caso de uso legítimo de iframe identificado na aplicação).
