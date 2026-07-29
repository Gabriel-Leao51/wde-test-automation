# language: pt
@visual
Funcionalidade: Regressão Visual - Páginas-chave da aplicação
  Como responsável pela qualidade da WDE Shop
  Eu quero comparar screenshots de páginas-chave com uma baseline aprovada
  Para detectar mudanças visuais não intencionais de layout/CSS

  Cenario: Página de login
    Quando eu visito a página de login
    Entao a página deve corresponder ao snapshot "login_page"

  Cenario: Catálogo de produtos
    Quando eu visito o catálogo de produtos
    Entao a página deve corresponder ao snapshot "products_catalog"

  Cenario: Página de detalhes do produto
    Quando eu visito a página de detalhes do produto "000000000000000000000001"
    Entao a página deve corresponder ao snapshot "product_details"

  Cenario: Painel de gerenciamento de produtos do admin
    Dado que eu estou logado como "admin"
    Quando eu visito o painel de gerenciamento de produtos
    Entao a página deve corresponder ao snapshot "admin_manage_products"

  Cenario: Página de erro 401
    Quando eu tento acessar uma página protegida sem estar logado
    Entao a página deve corresponder ao snapshot "error_401"
