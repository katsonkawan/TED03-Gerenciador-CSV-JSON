"""Leitura/escrita de JSON UTF-8, com rejeição de chaves duplicadas."""

import json
from pathlib import Path

from .excecoes import DadosInvalidosError
from .validacao import validar_registros


def _objeto_sem_chaves_duplicadas(pares: list[tuple[str, object]]) -> dict:
    resultado = {}
    for chave, valor in pares:
        if chave in resultado:
            raise DadosInvalidosError(f"JSON contém chave repetida: '{chave}'.")
        resultado[chave] = valor
    return resultado


def ler_json(caminho: str | Path) -> list[dict[str, str]]:
    with open(caminho, "r", encoding="utf-8-sig") as arquivo:
        registros = json.load(arquivo, object_pairs_hook=_objeto_sem_chaves_duplicadas)
    return validar_registros(registros)


def escrever_json(caminho: str | Path, registros: list[dict[str, str]]) -> None:
    validar_registros(registros)
    with open(caminho, "x", encoding="utf-8") as arquivo:
        json.dump(registros, arquivo, ensure_ascii=False, indent=2)
        arquivo.write("\n")
        arquivo.flush()
