# language: pt
Funcionalidade: Segurança Avançada - Hardening da Aplicação

  Como uma aplicação que processa dados de usuários e pagamentos
  Devo me proteger contra técnicas comuns de ataque e evitar vazar detalhes internos
  Para garantir a integridade, disponibilidade e confidencialidade do sistema

  @security @injection @happy-path
  Cenario: Tentativa de NoSQL injection no login não derruba a aplicação nem contorna a autenticação
    Quando eu envio um payload de NoSQL injection para "/login"
    Entao eu devo receber uma resposta de credenciais invalidas
    E a aplicacao deve permanecer no ar

  @security @injection @happy-path
  Cenario: Tentativa de NoSQL injection no cadastro não derruba a aplicação
    Quando eu envio um payload de NoSQL injection para "/signup"
    Entao a aplicacao deve permanecer no ar

  # BUG CONHECIDO (BUG-SEC-002): headers de segurança ausentes
  @security @headers @xfail
  Cenario: A aplicação deve responder com headers de segurança padrão
    Quando eu faco uma requisicao GET para "/products"
    Entao a resposta deve conter o header "x-content-type-options" com valor "nosniff"
    E a resposta deve conter o header "x-frame-options"
    E a resposta deve conter o header "content-security-policy"
    E a resposta nao deve conter o header "x-powered-by"

  # BUG CONHECIDO (BUG-SEC-003): token CSRF exposto na URL do formulário
  @security @csrf @xfail
  Cenario: O token CSRF não deve ser exposto na URL do formulário de produto
    Dado que eu estou logado como "admin"
    Quando eu visito a pagina de novo produto
    Entao o atributo action do formulario nao deve conter "_csrf"

  # BUG CONHECIDO (BUG-SEC-004): cookie de sessão sem flags Secure/SameSite
  @security @session @xfail
  Cenario: O cookie de sessão deve ter as flags Secure e SameSite configuradas
    Quando eu faco uma requisicao GET para "/login"
    Entao o cookie de sessao deve ter a flag Secure habilitada
    E o cookie de sessao deve ter a flag SameSite configurada

  # BUG CONHECIDO (BUG-INFO-001): mensagens de erro expõem detalhes internos do servidor
  @security @error-handling @xfail
  Cenario: Erros internos não devem expor caminhos e código-fonte do servidor
    Quando eu envio uma requisicao que causa um erro interno no servidor
    Entao a resposta nao deve conter caminhos do sistema de arquivos do servidor
    E a resposta nao deve conter trechos de codigo-fonte do servidor

  # BUG CONHECIDO (BUG-SEC-005): segredo de sessão hardcoded permite forjar cookies válidos
  @security @session @xfail
  Cenario: Um cookie de sessão forjado com o segredo hardcoded não deve conceder acesso
    Quando eu forjo um cookie de sessao de administrador usando o segredo hardcoded do codigo-fonte
    E eu acesso "/admin/products" usando apenas o cookie forjado
    Entao o acesso NAO deve ser concedido sem um login de verdade
