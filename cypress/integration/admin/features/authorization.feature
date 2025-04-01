# language: pt
Funcionalidade: Segurança - Autorização do Painel Administrativo
  Como um usuário cliente logado (sem permissões de admin)
  Eu não devo conseguir acessar páginas ou funcionalidades do painel administrativo
  Para garantir que apenas administradores gerenciem a loja

  Contexto: Usuário cliente logado
    Dado que eu estou logado como "cliente"

  # BUG CONHECIDO: Este cenário DEVE FALHAR se o bug persistir
  Cenario: Tentativa de acesso direto a Produtos do Admin por usuário cliente
    Quando eu tento acessar a URL "/admin/products"
    Então eu NÃO devo conseguir acessar a página de Produtos do Admin

  # Verificar proteção da área de Pedidos
  Cenario: Tentativa de acesso direto a Pedidos do Admin por usuário cliente
    Quando eu tento acessar a URL "/admin/orders"
    Então eu devo ver uma mensagem indicando falta de autorização

  # BUG CONHECIDO: Este cenário DEVE FALHAR se o bug persistir
  Cenario: Tentativa de acesso direto ao formulário de Edição de Produto por usuário cliente
    Quando eu tento acessar a URL "/admin/products/67b7b3be6110ce32e963ee77"
    Então eu NÃO devo conseguir acessar o formulário de Edição de Produto