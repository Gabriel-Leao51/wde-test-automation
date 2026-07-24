# BUG-INFO-001: Exposição de Detalhes Internos do Servidor em Páginas de Erro

## Severidade

**ALTA**

- **Justificativa:** Qualquer erro não tratado (não só o cenário reproduzido aqui) expõe caminhos completos do sistema de arquivos do servidor, trechos de código-fonte dos templates EJS e stack traces do Node.js diretamente ao cliente — inclusive a usuários não autenticados. Facilita reconhecimento (fingerprinting) da stack e da estrutura interna da aplicação para um atacante planejar outros ataques.

## Prioridade

**ALTA**

## Ambiente

- **Aplicação:** WDE Shop
- **URL Base:** `http://localhost:3000` (stack local via Docker Compose, ver `wde/docker-compose.yml`)
- **Endpoint Afetado:** qualquer rota que dispare uma exceção não tratada e caia no `errorHandlerMiddleware` — reproduzido aqui via `POST /cart/items` sem token CSRF válido
- **Perfil de Usuário:** não autenticado (não requer login)

## Detalhes do Relato

- **Relatado por:** Gabriel Leão (com assistência de Claude)
- **Data da Descoberta:** 24/07/2026
- **Contexto:** encontrado durante expansão da cobertura de segurança da suíte de testes, ao investigar o comportamento de `csurf` para requisições sem token CSRF válido.

## Passos para Reproduzir

1. Sem estar autenticado, envie uma requisição `POST` para um endpoint protegido por CSRF (ex: `/cart/items`) **sem** incluir o parâmetro `_csrf`:
   ```bash
   curl -X POST http://localhost:3000/cart/items --data-urlencode "productId=<id-valido>"
   ```
2. Observe a resposta HTTP.

## Resultado Esperado

- Uma resposta de erro genérica (idealmente `403 Forbidden` para token CSRF inválido/ausente), sem detalhes de implementação, caminhos de arquivo ou stack traces.

## Resultado Atual (Falha)

- A resposta é `500 Internal Server Error` contendo o HTML completo do handler de erro padrão do Express, incluindo:
  - Caminhos absolutos do servidor (`/usr/src/app/views/shared/500.ejs`, `/usr/src/app/views/shared/includes/header.ejs`, etc.)
  - Trechos do código-fonte dos templates EJS
  - Stack trace completo, incluindo caminhos de `node_modules`

Trecho real da resposta capturada:

```
TypeError: /usr/src/app/views/shared/500.ejs:4
    2| </head>
    3| <body>
 >> 4|   <%- include('includes/header') %>
...
Cannot read properties of undefined (reading 'totalQuantity')
    at eval ("/usr/src/app/views/shared/includes/nav-items.ejs":15:38)
    ...
```

## Evidências

- **Teste Automatizado:** `features/security/hardening.feature`, cenário "Erros internos não devem expor caminhos e código-fonte do servidor" (`@xfail`, tag `@error-handling`) — falha intencionalmente contra o comportamento atual, comprovando a exposição.
- **Reprodução manual:** comando `curl` acima, testado em 24/07/2026 contra a stack local.

## Análise de Causa Raiz

Duas causas se combinam para produzir esse resultado:

1. **`NODE_ENV` nunca é definido como `production`** em nenhum lugar (`Dockerfile`, `docker-compose.yml`, ou no próprio código da aplicação). O Express usa modo de desenvolvimento por padrão, que inclui detalhes verbosos de erro nas respostas — comportamento correto para depuração local, mas nunca desabilitado antes do deploy/execução "real" da stack.
2. **Falha em cascata no próprio handler de erro:** `middlewares/error-handler.js` tenta renderizar `views/shared/500.ejs`, que inclui `header.ejs` → `nav-items.ejs`. Esse último template lê `locals.cart.totalQuantity` incondicionalmente. Como `csurf()` é registrado em `app.js` **antes** de `cartMiddleware`, uma rejeição de CSRF nunca chega a popular `res.locals.cart` — a própria renderização da página de erro lança uma nova exceção, e o Express recorre ao seu handler de erro padrão (que é quem efetivamente vaza os detalhes internos).

Importante: esse encadeamento específico **não derruba o processo Node** (diferente do bug de NoSQL injection já corrigido) — é uma falha síncrona durante a renderização, capturada pelo próprio Express. O problema é puramente de exposição de informação e de UX de erro quebrada, não de disponibilidade.

## Impacto Potencial

- Vazamento de estrutura interna do servidor e da aplicação, útil para um atacante mapear a stack tecnológica e planejar ataques mais direcionados.
- Qualquer outro erro não tratado no restante da aplicação está sujeito ao mesmo vazamento, não apenas o caminho de CSRF usado para reproduzir aqui.
- Usuários finais veem uma página de erro genuinamente quebrada (a página de erro da própria aplicação falha ao renderizar) em vez de uma mensagem amigável.

## Recomendações

1. Definir `NODE_ENV=production` na configuração de execução da stack (`docker-compose.yml` do repositório `wde`), garantindo que o Express não exponha detalhes de erro em nenhum ambiente que não seja explicitamente de desenvolvimento local.
2. Corrigir `nav-items.ejs` para não presumir que `locals.cart` sempre existe (ex: `locals.cart?.totalQuantity || 0`, ou garantir um valor padrão em `res.locals` antes de qualquer possibilidade de erro).
3. Padronizar o `errorHandlerMiddleware` para nunca deixar uma falha na própria renderização da página de erro escapar para o handler padrão do Express — por exemplo, envolvendo o `res.render` em try/catch com um fallback em texto puro.
4. Garantir que erros de CSRF retornem um código de status mais preciso (`403`) em vez do genérico `500`.
