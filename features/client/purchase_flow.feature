# language: pt
Funcionalidade: Fluxo de Compra E2E do Cliente

  Como um cliente registrado da WDE Shop
  Eu quero encontrar um produto específico, adicioná-lo ao carrinho,
  e finalizar a compra usando pagamento de teste
  Para garantir que o processo principal de aquisição funciona corretamente

  Contexto: Cliente está logado
    Dado que eu estou logado como "cliente"

  Cenario: Cliente realiza compra de um produto específico com sucesso
    Quando eu clico em "View Details" para o produto "GTRACING - Black Gaming Chair"
    E eu clico no botão "Add to Cart" na página de detalhes do produto
    Entao o indicador do carrinho na barra de navegação deve ser atualizado para "1"
    Quando eu clico no link "Cart" da barra de navegação
    Entao eu devo ver o produto "GTRACING - Black Gaming Chair" listado no carrinho
    Quando eu clico no botão "Buy Products"
    Entao eu devo ser redirecionado para a página de pagamento externa do Stripe