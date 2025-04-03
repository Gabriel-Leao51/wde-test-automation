Relatório de Bug

ID do Bug: BUG-AUTH-002 (Sugestão, pode seguir o padrão que preferir)

Título: Falha de Autorização Parcial: Cliente Acessa Página /admin/orders com Funcionalidade Limitada e Potencial Vazamento de Dados

Severidade: Alta (Justificativa: Embora a modificação direta esteja aparentemente impedida, o acesso indevido a uma área administrativa e o risco significativo de visualização não autorizada de dados sensíveis (pedidos de outros clientes) elevam a severidade.)

Prioridade: Alta (Justificativa: Requer investigação e correção urgentes devido ao risco de exposição de dados e à quebra do controle de acesso.)

Ambiente:

Aplicação: WDE Shop

URL Base: [https://wde-5p3f.onrender.com]

Endpoint Afetado: /admin/orders

Perfil de Usuário: cliente

Navegador/Executor: Conforme execução do Cypress (Ex: Chrome vXX, Electron vYY)

Ambiente de Teste: Local (Cypress Runner) / CI (GitHub Actions)

Relatado por: Gabriel leão

Data da Descoberta: 31/03/2025

Passos para Reproduzir:

Faça login na aplicação WDE Shop utilizando credenciais de um usuário com perfil cliente.

Após o login bem-sucedido, navegue diretamente para a URL [URL Base]/admin/orders na barra de endereços do navegador.

(Alternativa via Automação: Execute o cenário "Cliente logado tenta acessar a página de gerenciamento de pedidos" no arquivo cypress/integration/admin/features/authorization.feature)

Resultado Esperado:

O usuário com perfil cliente não deve conseguir acessar ou visualizar qualquer conteúdo da página /admin/orders. A aplicação deve:

Redirecionar o usuário para uma página de erro de autorização padrão (ex: /401, /403) OU

Redirecionar o usuário para sua página inicial de cliente (ex: /) E

Exibir uma mensagem clara informando que o acesso àquela seção não é permitido para seu perfil.

Resultado Atual:

O usuário com perfil cliente consegue carregar a URL /admin/orders sem ser redirecionado para uma página de erro de acesso negado (como /401 ou /403).

A página é renderizada de forma parcial ou incompleta:

Elementos visuais chave da interface administrativa (como o título principal da seção "Pedidos") podem estar ausentes.

Controles específicos para manipulação de dados (como o dropdown para alterar status do pedido e o botão para submeter a alteração) não são exibidos ou estão desabilitados.

Mais importante: Apesar da ausência dos controles de modificação, a estrutura base da página de listagem de pedidos é carregada. Existe um risco considerável de que a lista de pedidos (potencialmente incluindo pedidos de outros usuários) esteja sendo exibida nesta visão parcial, caracterizando um vazamento de dados.

Nenhuma mensagem explícita de "Não Autorizado" que bloqueie completamente a visualização do conteúdo da página é exibida de forma proeminente (a menos que o teste automatizado esteja validando algum texto específico presente nesta página quebrada).
