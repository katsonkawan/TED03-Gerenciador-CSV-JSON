"""Conversão segura e sem perda de texto entre CSV e JSON."""

from pathlib import Path

from .excecoes import DadosInvalidosError
from .persistencia import ler_registros, salvar_registros


def converter(origem: str | Path, destino: str | Path) -> tuple[int, Path | None]:
    entrada, saida = Path(origem), Path(destino)
    if entrada.suffix.lower() not in (".csv", ".json"):
        raise DadosInvalidosError("O arquivo de origem deve ser CSV ou JSON.")
    esperado = ".json" if entrada.suffix.lower() == ".csv" else ".csv"
    if saida.suffix.lower() != esperado:
        raise DadosInvalidosError(
            f"Conversão inválida: de {entrada.suffix.lower()} para {esperado}."
        )
    if entrada.resolve() == saida.resolve():
        raise DadosInvalidosError("Origem e destino devem ser arquivos diferentes.")

    registros = ler_registros(entrada)
    copia = salvar_registros(saida, registros)
    return len(registros), copia
