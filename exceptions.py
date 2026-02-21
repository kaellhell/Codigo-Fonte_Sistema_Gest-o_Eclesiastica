class ContatoError(Exception):
    """Classe base para erros de contatos."""
    pass

class ContatoDuplicadoError(ContatoError):
    pass

class ContatoNaoEncontradoError(ContatoError):
    pass