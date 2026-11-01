"""Leitura, escrita atômica, backup e atualização de registros."""

from pathlib import Path
import os
from uuid import uuid4

from .backup import criar_backup
from .excecoes import DadosInvalidosError
from .io_csv import escrever_csv, ler_csv
from .io_json import escrever_json, ler_json
from .validacao import validar_registros


LEITORES = {".csv": ler_csv, ".json": ler_json}
ESCRITORES = {".csv": escrever_csv, ".json": escrever_json}


def _verificar_formato(caminho: str | Path) -> str:
    extensao = Path(caminho).suffix.lower()
    if extensao not in LEITORES:
        raise DadosInvalidosError("Formato inválido: utilize arquivo .csv ou .json.")
    return extensao


def ler_registros(caminho: str | Path) -> list[dict[str, str]]:
    extensao = _verificar_formato(caminho)
    return LEITORES[extensao](caminho)


def salvar_registros(caminho: str | Path, registros: list[dict[str, str]]) -> Path | None:
    """Efetua backup se arquivo existe, grava temporário e substitui atomicamente.

    Em caso de falha no backup, NÃO escreve o destino. Em caso de falha durante
    a escrita, preserva o destino anterior e apaga somente o temporário.
    """
    destino = Path(caminho)
    extensao = _verificar_formato(destino)
    validar_registros(registros)

    if not destino.parent.is_dir():
        raise FileNotFoundError(f"Pasta de destino não encontrada: {destino.parent}")
    if destino.exists() and not destino.is_file():
        raise DadosInvalidosError(f"Destino não é um arquivo comum: {destino}")

    copia = criar_backup(destino) if destino.exists() else None
    temporario = destino.with_name(f".{destino.name}.{uuid4().hex}.tmp")
    try:
        ESCRITORES[extensao](temporario, registros)
        # Em um mesmo sistema de arquivos, os.replace substitui o destino atomicamente.
        os.replace(temporario, destino)
    finally:
        temporario.unlink(missing_ok=True)
    return copia


def atualizar_registro(
    caminho: str | Path, identificador: str, campo: str, novo_valor: str
) -> tuple[bool, Path | None]:
    """Atualiza exatamente um registro identificado por 'id', sem alterar outros."""
    registros = ler_registros(caminho)
    if "id" not in registros[0]:
        raise DadosInvalidosError("Não é possível atualizar: campo 'id' ausente.")
    if campo not in registros[0]:
        raise DadosInvalidosError(f"Campo inexistente: '{campo}'.")
    encontrados = [r for r in registros if r["id"] == identificador]
    if not encontrados:
        raise DadosInvalidosError(f"Nenhum registro encontrado com id '{identificador}'.")
    if len(encontrados) > 1:
        raise DadosInvalidosError(f"ID duplicado: '{identificador}'. Atualização cancelada.")
    if encontrados[0][campo] == novo_valor:
        return False, None

    encontrados[0][campo] = novo_valor
    copia = salvar_registros(caminho, registros)
    return True, copia
