# language: pt
Funcionalidade: Gerenciar Produtos - Painel Administrativo

    Como um administrador logado
    Eu quero ser capaz de gerenciar produtos no painel administrativo
    Para manter o catalogo da loja atualizado

    Contexto:
        Dado que eu estou logado como "admin"
        E eu estou na pagina inicial do painel administrativo "/products"
        Quando eu navego para a pagina de gerenciamento de produtos "Manage Products"

    @crud @product @happy-path
    Cenario: Adicionar um novo produto com sucesso
        Quando eu clico no botao "Add Product"
        E eu preencho o formulario de adicionar produto com os seguintes dados:
            | Campo       | Valor                                    |
            | title       | Mousepad Teste                           |
            | image       | mousepad.jpg                             |
            | summary     | Um ótimo mousepad para teste             |
            | price       | 35                                       |
            | description | Mousepad ideal para testes automatizados |
        E eu clico no botao "Save"
        Entao eu devo ser redirecionado para a pagina de gerenciamento de produtos "/admin/products"
        E o produto "Mousepad Teste" deve estar visivel na listagem de produtos com titulo e imagem

    @crud @product @happy-path
    Cenario: Editar um produto existente com sucesso
        Quando eu clico no botao "View & Edit" para o produto de titulo "Mousepad Teste"
        E eu preencho o formulario de edição de produto com os seguintes dados:
            | Campo       | Valor                                                         |
            | title       | Mousepad Teste Editado                                        |
            | summary     | Resumo Editado do Mousepad de Teste                           |
            | price       | 40                                                            |
            | description | Descrição Editada do Mousepad ideal para testes automatizados |
        E eu clico no botao "Save"
        Entao eu devo ser redirecionado para a pagina de gerenciamento de produtos "/admin/products"
        E o produto "Mousepad Teste Editado" deve ser exibido na listagem de produtos com o titulo atualizado

    @crud @product @happy-path
    Cenario: Excluir um produto existente com sucesso
        Quando eu clico no botao "Delete" para o produto de titulo "Mousepad Teste Editado"
        Entao o produto "Mousepad Teste Editado" não deve ser mais exibido na listagem de produtos

    @validation @product @negative-path
    Cenario: Adicionar um produto com campo obrigatório nome em branco
        Quando eu clico no botao "Add Product"
        E eu preencho o formulario de adicionar produto com os seguintes dados:
            | Campo       | Valor |
            | image       | mousepad.jpg                             |
            | summary     | Um ótimo mousepad para teste             |
            | price       | 35                                       |
            | description | Mousepad ideal para testes automatizados |
        E eu clico no botao "Save"
        Entao eu devo ver uma mensagem de erro informando que os campos obrigatorios devem ser preenchidos
        E eu devo permanecer na pagina de adicionar produto