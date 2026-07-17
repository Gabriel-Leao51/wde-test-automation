#language: pt
Funcionalidade: Gerenciar Pedidos - Painel Administrativo

    Como um administrador logado
    Eu quero ser capaz de gerenciar o status de pedidos no painel administrativo
    Para manter o controle de vendas da loja atualizado

    Contexto:
        Dado que eu estou logado como "admin"
        E eu navego para a pagina de gerenciamento de pedidos

    @crud @order @happy-path
    Cenario: Alterar status de um pedido para "Fulfilled" com sucesso
        Dado que um pedido com status "Pending" conhecido existe
        Quando eu localizo o pedido conhecido na lista de pedidos
        E eu seleciono o novo status "Fulfilled" para este pedido
        E eu clico no botao "Update" deste pedido
        Entao o status "FULFILLED" deve ser exibido para este pedido
