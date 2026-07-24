# BUG-SEC-004: Cookie de Sessão sem Flags `Secure`/`SameSite`

## Severidade

**MÉDIA**

- **Justificativa:** O cookie de sessão (`connect.sid`) já possui `HttpOnly` (protege contra roubo via XSS), mas não define explicitamente `Secure` nem `SameSite`. Sem `Secure`, o cookie pode ser transmitido em texto claro caso a aplicação seja um dia servida também por HTTP além de HTTPS. Sem `SameSite` explícito, a aplicação depende do comportamento padrão do navegador do cliente em vez de impor a política, o que é inconsistente entre navegadores/versões.

## Prioridade

**MÉDIA**

## Ambiente

- **Aplicação:** WDE Shop
- **URL Base:** `http://localhost:3000`
- **Endpoint Afetado:** qualquer resposta que defina o cookie de sessão (ex: `GET /login`)

## Detalhes do Relato

- **Relatado por:** Gabriel Leão (com assistência de Claude)
- **Data da Descoberta:** 24/07/2026

## Passos para Reproduzir

```bash
curl -I http://localhost:3000/login
```

## Resultado Esperado

O header `Set-Cookie` deve incluir as flags `Secure` e `SameSite=Strict` (ou `Lax`, dependendo da necessidade de navegação cross-site) além de `HttpOnly`.

## Resultado Atual (Falha)

Resposta real capturada:

```
Set-Cookie: connect.sid=s%3A...; Path=/; Expires=...; HttpOnly
```

Apenas `HttpOnly` está presente. `Secure` e `SameSite` estão ausentes.

## Evidências

- **Teste Automatizado:** `features/security/hardening.feature`, cenário "O cookie de sessão deve ter as flags Secure e SameSite configuradas" (`@xfail`, tag `@session`).
- **Reprodução manual:** comando `curl -I` acima.

## Análise de Causa Raiz

`config/session.js` configura o cookie apenas com `maxAge`:

```js
cookie: {
  maxAge: 2 * 24 * 60 * 60 * 1000,
},
```

Nenhuma opção `secure` ou `sameSite` é passada ao `express-session`.

## Impacto Potencial

- Sem `Secure`, o cookie de sessão pode trafegar sem criptografia se a aplicação for exposta também via HTTP em algum ambiente.
- Sem `SameSite` explícito, a proteção contra CSRF que o navegador ofereceria nativamente para requisições cross-site fica sujeita ao comportamento padrão (varia por navegador/versão) em vez de ser garantida pela aplicação.

## Recomendações

1. Em `config/session.js`, definir explicitamente `cookie: { maxAge: ..., secure: true, sameSite: 'lax' }` (ou `'strict'`, avaliando se algum fluxo legítimo depende de navegação cross-site — ex: retorno do Stripe Checkout).
2. Como o app roda atrás de HTTPS apenas em produção, considerar tornar `secure` condicional ao ambiente (`process.env.NODE_ENV === 'production'`) para não quebrar o desenvolvimento local via HTTP — mas isso deve vir acompanhado da correção de `BUG-INFO-001` (definir `NODE_ENV` corretamente).
