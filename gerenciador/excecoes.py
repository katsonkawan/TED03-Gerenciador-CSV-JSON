"""Exceções específicas para identificar dados inconsistentes."""


class DadosInvalidosError(ValueError):
    """Arquivo estruturalmente inválido ou incompatível com conversão sem perdas."""
