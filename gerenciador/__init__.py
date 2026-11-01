"""Pacote de persistência segura e conversão CSV/JSON."""

from .conversao import converter
from .persistencia import atualizar_registro, ler_registros

__all__ = ["converter", "atualizar_registro", "ler_registros"]
