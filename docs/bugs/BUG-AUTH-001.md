# BUG-AUTH-001: Falha Crítica de Autorização - Acesso Indevido a CRUD de Produtos por Cliente

## Severidade

**CRÍTICA (ALTO RISCO)**

- **Justificativa:** Vulnerabilidade de segurança extremamente grave. Permite que usuários não autorizados (`cliente`) manipulem **completamente** o catálogo de produtos (adição e edição), levando a potenciais danos financeiros, operacionais, reputacionais e legais catastróficos e generalizados para a loja online.

## Prioridade

**IMEDIATA (MÁXIMA URGÊNCIA / EMERGÊNCIA)**

- **Justificativa:** Dada a severidade CRÍTICA e o potencial impacto devastador, a resolução deve ser tratada como uma emergência absoluta, com interrupção de outras tarefas para foco na correção.

## Ambiente

- **Aplicação:** WDE Shop
- **URL Base:** `https://wde-5p3f.onrender.com`
- **Endpoints Afetados:**
  - `/admin/products` (permite acesso ao botão "Add product" e visualização)
  - `/admin/products/add` (acesso direto ao formulário de adição - inferido)
  - `/admin/products/edit/:id` (acesso direto ao formulário de edição)
- **Perfil de Usuário:** `cliente` (não administrativo)
- **Navegador/OS:** Google Chrome v.134 (ou conforme execução Cypress), Windows 11
- **Ambiente de Teste:** Local (Cypress Runner) / CI (GitHub Actions) / Manual (Render)

## Detalhes do Relato

- **Relatado por:** Gabriel Leão
- **Data da Descoberta:** 19/03/2025
- **Referência Original:** TC_ADMIN_SECURITY_033 (Jira/Test Case ID)

## Passos para Reproduzir

1.  Faça login na aplicação WDE Shop (`https://wde-5p3f.onrender.com`) utilizando credenciais de um usuário com perfil `cliente` (ex: `user@example.com` / `usertest`).
2.  Após o login bem-sucedido (na área do cliente), modifique a URL na barra de endereços do navegador para acessar diretamente os endpoints administrativos:
    - Para listar produtos e acessar o botão "Add": `https://wde-5p3f.onrender.com/admin/products`
    - Para editar um produto (substitua `:id` por um ID válido): `https://wde-5p3f.onrender.com/admin/products/edit/:id`
    - _Implícito/Provável:_ Para adicionar um produto diretamente: `https://wde-5p3f.onrender.com/admin/products/new`
3.  Observe se o acesso é concedido e se é possível interagir com os formulários de adição/edição.
4.  **(Opcional/Confirmação):** Tente efetivamente salvar uma alteração em um produto existente ou adicionar um novo produto.
5.  **(Alternativa via Automação):** Execute os cenários correspondentes em `cypress/integration/admin/features/authorization.feature` que tentam acessar `/admin/products` e `/admin/products/edit/:id` como `cliente`.

## Resultado Esperado (Conforme TC_ADMIN_SECURITY_033)

- O usuário `cliente` **NÃO deve** conseguir acessar nenhuma das páginas/funcionalidades administrativas de produtos (`/admin/products`, `/admin/products/add`, `/admin/products/edit/:id`).
- O usuário deve ser redirecionado para uma página de erro de autorização (ex: `/403 Forbidden` ou `/401 Unauthorized`).
- Uma mensagem clara como "Not authorized - you are not authorized to access this page!" deve ser exibida, informando a falta de permissão.

## Resultado Atual (Falha Crítica de Segurança)

- **FALHA:** O usuário `cliente` **CONSEGUE** acessar as páginas/formulários de listagem, adição e edição de produtos no painel administrativo.
- **FALHA:** O usuário **NÃO é redirecionado** para uma página de erro 403/401. O acesso aos formulários é direto.
- **FALHA:** Nenhuma mensagem de "Não autorizado" é exibida.
- **CONFIRMAÇÃO GRAVE:** Foi confirmado que o usuário `cliente` pode não apenas visualizar, mas **EFETIVAMENTE ADICIONAR NOVOS PRODUTOS e EDITAR PRODUTOS EXISTENTES** através destes formulários acessados indevidamente. A manipulação completa do catálogo é possível.

## Evidências

- **Teste Automatizado (`authorization.feature`):** Os cenários correspondentes falham intencionalmente ao tentar acessar as URLs como `cliente`, comprovando a falha de redirecionamento/bloqueio esperado.
- **Verificação Manual:** Acesso direto às URLs confirma a renderização das páginas administrativas para o perfil `cliente` e a capacidade de interação com os formulários.
- **Screenshots/Vídeos:** `[![Painel Admin Exposto (BUG-AUTH-001)](evidence/BUG-AUTH-001-Admin-panel-exposed.png)
![Formulário de Adição de Produto Exposto](evidence/BUG-AUTH-001-Add-product-form-exposed.png)
![Formulário de Edição Exposto (BUG-AUTH-001)](evidence/BUG-AUTH-001-Edit-product-form-exposed.png)
[Vídeo da Execução dos Testes de Autorização](evidence/authorization.feature.mp4)]` - Screenshots/vídeos mostrando o acesso do cliente aos formulários de admin e, idealmente, a confirmação de uma adição/edição bem-sucedida.

## Análise de Causa Raiz (Provável)

- Ausência **total ou falha crítica** na implementação de verificação de **autorização (permissões/role)** no backend para as rotas e funcionalidades de gerenciamento de produtos (`/admin/products/*`).
- A proteção pode estar baseada apenas em **autenticação** (usuário logado), ignorando completamente o perfil/role (`admin` vs `cliente`) necessário para acessar estas funções.

## Impacto Potencial (Catastrófico)

- **Manipulação e Corrupção Total de Dados de Produtos:**
  - Alteração massiva de preços (para zero, valores absurdos).
  - Modificação de descrições/títulos com conteúdo falso, ofensivo, ilegal.
  - Substituição de imagens por conteúdo impróprio/ilegal.
  - **Adição de produtos falsos, ilegais, spam, ou de concorrentes.**
- **Danos Financeiros Catastróficos:** Vendas com prejuízo, multas, perda de receita e investidores.
- **Danos Reputacionais Irreversíveis:** Perda total de confiança do cliente, destruição da imagem da marca.
- **Problemas Operacionais Insuportáveis:** Caos na gestão de estoque, pedidos, atendimento ao cliente.
- **Riscos Legais Graves:** Processos devido a conteúdo ilegal, produtos falsos, violação de termos.

## Recomendações (Ações Urgentes e Extremas)

1.  **CORREÇÃO IMEDIATA:** Implementar um sistema de **autorização baseado em roles (perfis)** robusto e intransigente no **backend** para TODAS as rotas e operações dentro de `/admin/*`, bloqueando completamente o acesso não autorizado (especialmente para `cliente`).
2.  **VERIFICAÇÃO OBRIGATÓRIA:** Garantir que a checagem de autorização ocorra em **cada requisição** ao backend para funcionalidades administrativas, sem exceção.
3.  **REVISÃO DE SEGURANÇA URGENTE:** Realizar uma auditoria de segurança completa por especialistas em toda a aplicação, focando em controle de acesso e autorização.
4.  **TESTES AUTOMATIZADOS:** Implementar testes de segurança automatizados **extensivos** (focando em autorização para todas as roles e rotas admin) no pipeline de CI/CD para prevenir regressões.
5.  **MEDIDA DE CONTENÇÃO (Considerar):** Avaliar a necessidade **imediata** de colocar o painel `/admin` offline ou restringir o acesso **apenas** a um grupo mínimo de administradores confiáveis **até que a correção seja implementada e validada**, dada a gravidade extrema da falha.
