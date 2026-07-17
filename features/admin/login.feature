# language: pt
Funcionalidade: Login Administrativo
    Como um administrador
    Eu quero fazer login no painel administrativo
    Para acessar as funcionalidades de gerenciamento do sistema

    @auth @login-admin @happy-path
    Cenario: Login administrativo bem-sucedido
        Dado que eu estou na pagina de login administrativo
        Quando eu insiro um email de administrador valido 
        E eu insiro uma senha de administrador valida
        E eu clico no botao de "Login"
        Entao eu devo ser redirecionado para a pagina principal do painel administrativo
        E eu devo ver as opcoes de menu "Manage Products" e "Manage Orders"
        E eu devo ver o botao "Logout" no cabecalho

    @auth @login-admin @negative-case  
    Cenario: Login administrativo falha - Credenciais invalidas
        Dado que eu estou na pagina de login
        Quando eu insiro um email invalido
        E eu insiro uma senha invalida
        E eu clico no botão de "Login"
        Entao eu devo ver uma mensagem de erro
        E eu devo permanecer na pagina de login