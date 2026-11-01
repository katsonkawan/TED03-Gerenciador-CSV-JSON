"""Backup binário, criado e concluído ANTES de modificar o original."""

from datetime import datetime
from pathlib import Path
import os
import shutil
from uuid import uuid4


def criar_backup(caminho: str | Path) -> Path:
    origem = Path(caminho)
    pasta = origem.parent / "backups"
    pasta.mkdir(parents=True, exist_ok=True)
    momento = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    copia = pasta / f"{origem.name}.{momento}_{uuid4().hex[:8]}.bak"

    try:
        # Ambos os arquivos são gerenciados com with open.
        with open(origem, "rb") as entrada, open(copia, "xb") as saida:
            shutil.copyfileobj(entrada, saida)
            saida.flush()
            os.fsync(saida.fileno())
    except OSError:
        copia.unlink(missing_ok=True)  # Não deixar um backup parcial como válido.
        raise

    return copia
