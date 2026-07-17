#language: pt
Funcionalidade: Segurança - Autenticação do Painel Administrativo
  Como um visitante não autenticado
  Eu não devo conseguir acessar páginas protegidas do painel administrativo
  Para garantir a segurança do sistema

  Cenario: Tentativa de acesso direto a Produtos do Admin sem estar logado
    Quando eu tento acessar a URL "/admin/products" sem estar logado
    Entao eu devo ser direcionado para a página de erro 401
    E eu devo ver os elementos da página de não autenticado

  Cenario: Tentativa de acesso direto a Pedidos do Admin sem estar logado
    Quando eu tento acessar a URL "/admin/orders" sem estar logado
    Entao eu devo ser direcionado para a página de erro 401
    E eu devo ver os elementos da página de não autenticado
