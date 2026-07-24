# BUG-SEC-003: Token CSRF Exposto na URL (Query String)

## Severidade

**MÉDIA-BAIXA**

- **Justificativa:** O token CSRF em si continua sendo validado corretamente pelo servidor (confirmado: requisições sem token ou com token inválido são rejeitadas — ver `BUG-INFO-001` para o problema *de resposta* a essa rejeição). O risco aqui é o **canal de exposição**: colocar o token na URL faz com que ele seja gravado em logs de acesso do servidor, no histórico do navegador, e potencialmente vazado a terceiros via header `Referer` quando a página carrega recursos externos.

## Prioridade

**MÉDIA**

## Ambiente

- **Aplicação:** WDE Shop
- **URL Base:** `http://localhost:3000`
- **Endpoint Afetado:** `/admin/products/new`, `/admin/products/:id` (formulário de produto) — o padrão de código responsável (`views/admin/products/includes/product-form.ejs`) é compartilhado por ambas as telas.

## Detalhes do Relato

- **Relatado por:** Gabriel Leão (com assistência de Claude)
- **Data da Descoberta:** 24/07/2026

## Passos para Reproduzir

1. Faça login como `admin`.
2. Acesse `/admin/products/new`.
3. Inspecione o atributo `action` do formulário de produto (ou observe a URL após um submit falho).

## Resultado Esperado

O token CSRF deve ser enviado apenas como campo oculto (`<input type="hidden" name="_csrf">`) dentro do corpo do formulário — nunca como parâmetro de URL.

## Resultado Atual (Falha)

`views/admin/products/includes/product-form.ejs` constrói a `action` do formulário assim:

```html
<form action="<%= submitPath %>?_csrf=<%= locals.csrfToken %>" method="POST" enctype="multipart/form-data">
```

O token aparece diretamente na URL de destino do formulário (ex: `/admin/products?_csrf=AbCdEf123...`).

## Evidências

- **Teste Automatizado:** `features/security/hardening.feature`, cenário "O token CSRF não deve ser exposto na URL do formulário de produto" (`@xfail`, tag `@csrf`).
- **Código-fonte:** `wde/views/admin/products/includes/product-form.ejs`.

Nota: os demais formulários da aplicação (login, carrinho, logout, pedidos) usam corretamente `<input type="hidden" name="_csrf" ...>` — este padrão problemático está isolado ao formulário de produto.

## Análise de Causa Raiz

O formulário de produto usa `enctype="multipart/form-data"` (necessário para upload de imagem). Aparentemente, o token foi colocado na URL como forma de garantir que ele fosse enviado independente da presença do arquivo — mas um campo oculto dentro do `<form multipart>` funciona normalmente e é o padrão usado em todos os outros formulários com upload/submit da aplicação.

## Impacto Potencial

- O token CSRF passa a constar em logs de acesso do servidor (geralmente retidos por mais tempo que a sessão em si).
- Fica registrado no histórico de navegação do navegador do administrador.
- Pode vazar via header `Referer` para qualquer recurso de terceiros carregado a partir dessa página (fontes, scripts, imagens externas).
- Reduz a eficácia da proteção CSRF caso o token vaze por qualquer um desses canais e ainda esteja válido na janela de sessão.

## Recomendações

1. Alterar `product-form.ejs` para usar `action="<%= submitPath %>"` (sem query string) e adicionar `<input type="hidden" name="_csrf" value="<%= locals.csrfToken %>">` dentro do formulário, no mesmo padrão já usado pelos demais formulários da aplicação.
