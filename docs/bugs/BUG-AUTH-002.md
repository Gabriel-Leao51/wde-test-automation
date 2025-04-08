# BUG-AUTH-002: Falha de Autorização - Cliente Acessa `/admin/orders` e Visualiza Pedidos Alheios

## Severidade

**Alta**

- **Justificativa:** Acesso indevido a uma área administrativa e a visualização confirmada de dados de pedidos pertencentes a outros usuários constituem uma violação de privacidade e segurança significativa, mesmo que PII direta não esteja visível nesta tela específica.

## Prioridade

**Alta**

- **Justificativa:** Requer investigação e correção urgentes devido à exposição confirmada de dados e à quebra do controle de acesso.

## Ambiente

- **Aplicação:** WDE Shop
- **URL Base:** `https://wde-5p3f.onrender.com`
- **Endpoint Afetado:** `/admin/orders`
- **Perfil de Usuário:** `cliente`
- **Navegador/Executor:** Conforme execução do Cypress (Ex: Chrome vXX, Electron vYY)
- **Ambiente de Teste:** Local (Cypress Runner) / CI (GitHub Actions)

## Detalhes do Relato

- **Relatado por:** Gabriel Leão
- **Data da Descoberta Original:** 31/03/2025
- **Data da Confirmação do Vazamento:** 03/04/2025

## Passos para Reproduzir

1.  **Pré-condição:** Certifique-se de que existam pedidos previamente criados por _outros usuários_ na base de dados para observar o vazamento claramente. (A execução do teste E2E `purchase_flow.feature` pode criar um desses pedidos).
2.  Faça login na aplicação WDE Shop (`https://wde-5p3f.onrender.com`) utilizando credenciais de um usuário com perfil `cliente`.
3.  Após o login bem-sucedido, navegue diretamente para a URL `https://wde-5p3f.onrender.com/admin/orders` na barra de endereços do navegador.
4.  **(Alternativa via Automação):** Execute o cenário correspondente em `cypress/integration/admin/features/authorization.feature` que tenta acessar `/admin/orders` como `cliente`.

## Resultado Esperado

O usuário com perfil `cliente` **não deve** conseguir acessar ou visualizar qualquer conteúdo da página `/admin/orders`. A aplicação deve:

- Redirecionar o usuário para uma página de erro de autorização padrão (ex: `/401`, `/403`)
- **OU** Redirecionar o usuário para sua página inicial de cliente (ex: `/`)
- **E** Exibir uma mensagem clara informando que o acesso àquela seção não é permitido para seu perfil.

## Resultado Atual

- O usuário com perfil `cliente` **consegue carregar** a URL `/admin/orders` sem ser redirecionado para uma página de erro de acesso negado (`/401` ou `/403`).
- A página é renderizada de forma **parcial ou incompleta**:
  - Elementos visuais chave da interface administrativa (como o título "Pedidos") podem estar ausentes.
  - Controles específicos para manipulação de dados (como o dropdown para alterar status do pedido e o botão para submeter a alteração) não são exibidos ou estão desabilitados.
- **VAZAMENTO DE DADOS CONFIRMADO:**
  - Apesar da ausência dos controles, a estrutura da lista de pedidos **é carregada e exibe pedidos pertencentes a outros usuários**.
  - Confirmação realizada manualmente após execução do teste E2E `purchase_flow.feature` (que criou um pedido para 'Cliente A'), onde um usuário diferente ('Cliente B', ou mesmo um usuário `admin`) logado acessando `/admin/orders` conseguiu visualizar detalhes do pedido do 'Cliente A' (produtos, data, status).
  - **Limitação Observada:** Informações de identificação pessoal (PII) diretas, como nome completo e endereço do cliente associado ao pedido, _não foram observadas_ nesta visualização específica de `/admin/orders` acessada pelo perfil `cliente`. No entanto, os detalhes do pedido são expostos.
- Nenhuma mensagem explícita de "Não Autorizado" que bloqueie completamente a visualização do conteúdo da página é exibida de forma proeminente.

## Evidências

- **Teste Automatizado (`authorization.feature`):** O cenário correspondente demonstra o acesso indevido à URL `/admin/orders` pelo perfil `cliente` (o teste pode falhar na asserção de redirecionamento esperado ou validar um status code incorreto). A _asserção específica de vazamento_ de dados de outros usuários não foi automatizada.
- **Geração de Dados:** O teste E2E `purchase_flow.feature` foi utilizado para criar um pedido de teste conhecido para um usuário `cliente`.
- **Verificação Manual:** Confirmação visual realizada acessando `/admin/orders` como outro usuário (`cliente` ou `admin`) após a geração do pedido de teste, observando a presença de pedidos não pertencentes ao usuário logado.
- **Screenshots/Vídeos:** `[![Painel Admin Acessado (BUG-AUTH-002)](evidence/BUG-AUTH-002-Admin-panel.png)
![Vazamento de Dados (Pedidos de Outros) (BUG-AUTH-002)](evidence/BUG-AUTH-002-Data-leak.png)
![Comportamento Esperado (Ex: Erro 403) (BUG-AUTH-002)](evidence/BUG-AUTH-002-Expected-behavior.png)
[Vídeo da Execução dos Testes de Autorização](evidence/authorization.feature.mp4)]` - Screenshots/vídeos da página `/admin/orders` acessada pelo `cliente`, destacando a presença de pedidos de outros usuários.
- **Link do CI/CD:** `[Link para a execução relevante no GitHub Actions, se aplicável]` - Execução mostrando a execução dos testes de autorização.

## Notas Adicionais / Ação Recomendada

- Esta descoberta confirma o risco de vazamento de dados anteriormente levantado como "potencial" para a rota `/admin/orders`.
- **Ação Principal:** Implementar uma verificação de autorização robusta no **backend** para a rota `/admin/orders`. Impedir completamente o acesso de usuários com perfil `cliente`, preferencialmente retornando um status `403 Forbidden` ou `401 Unauthorized` e/ou redirecionando no lado do servidor antes que a página ou dados sejam enviados ao frontend.
- **Ação Secundária (Contenção Frontend):** Como medida adicional (mas não substituta), o frontend também pode implementar uma verificação de perfil e redirecionar o usuário `cliente` caso ele tente acessar a rota `/admin/orders` diretamente.
- **Revisão de Segurança:** Recomenda-se uma revisão de segurança em _todas_ as rotas administrativas (`/admin/*`) para garantir que a validação de perfil (`admin` vs `cliente`) está sendo aplicada corretamente no backend.
