"""Leitura/escrita de CSV com codificação e validação explícitas."""

import csv
from pathlib import Path

from .excecoes import DadosInvalidosError
from .validacao import validar_registros


def ler_csv(caminho: str | Path) -> list[dict[str, str]]:
    """Lê CSV UTF-8, inclusive BOM, preservando texto, aspas e novas linhas."""
    with open(caminho, "r", encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.reader(arquivo, strict=True)
        try:
            cabecalho = next(leitor)
        except StopIteration as exc:
            raise DadosInvalidosError("CSV vazio: faltam cabeçalho e registros.") from exc
        if not cabecalho or any(not campo.strip() for campo in cabecalho):
            raise DadosInvalidosError("CSV possui nomes de campos vazios.")
        if len(cabecalho) != len(set(cabecalho)):
            raise DadosInvalidosError("CSV contém nomes de campos repetidos.")

        registros = []
        for numero_linha, valores in enumerate(leitor, start=2):
            if len(valores) != len(cabecalho):
                raise DadosInvalidosError(
                    f"CSV: registro {numero_linha} possui {len(valores)} campo(s); "
                    f"esperados {len(cabecalho)}."
                )
            registros.append(dict(zip(cabecalho, valores)))

    return validar_registros(registros)


def escrever_csv(caminho: str | Path, registros: list[dict[str, str]]) -> None:
    """Cria um novo arquivo CSV; o módulo de persistência gerencia a troca final."""
    validar_registros(registros)
    campos = list(registros[0].keys())
    with open(caminho, "x", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(
            arquivo, fieldnames=campos, extrasaction="raise", lineterminator="\n"
        )
        escritor.writeheader()
        escritor.writerows(registros)
        arquivo.flush()
