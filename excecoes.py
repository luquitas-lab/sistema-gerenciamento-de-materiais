class EstoqueException(Exception):
    """Classe base para todas as exceções do módulo de Estoque."""
    pass

class EstoqueInsuficienteError(EstoqueException):
    """Lançada quando tenta-se dar baixa em uma quantidade maior que o estoque atual."""
    pass

class MaterialNaoEncontradoError(EstoqueException):
    """Lançada quando uma operação solicita um ID de material inexistente ou inativo."""
    pass