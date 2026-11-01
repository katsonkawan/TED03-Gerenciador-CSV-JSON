"""Validação da estrutura tabular compartilhada por CSV e JSON."""

from .excecoes import DadosInvalidosError


def validar_registros(registros: object) -> list[dict[str, str]]:
    """Aceita lista não vazia de objetos com campos uniformes e valores texto.

    CSV não armazena tipos JSON (número, booleano, nulo). Recusar esses tipos
    evita conversão supostamente reversível que perderia informações de tipo.
    """
    if not isinstance(registros, list) or not registros:
        raise DadosInvalidosError("Os dados devem conter uma lista não vazia de registros.")

    if not isinstance(registros[0], dict) or not registros[0]:
        raise DadosInvalidosError("Cada registro deve ser um objeto com campos.")

    campos = list(registros[0].keys())
    if any(not isinstance(campo, str) or not campo.strip() for campo in campos):
        raise DadosInvalidosError("Todos os nomes de campos devem ser textos não vazios.")

    conjunto_campos = set(campos)
    for indice, registro in enumerate(registros, start=1):
        if not isinstance(registro, dict):
            raise DadosInvalidosError(f"Registro {indice}: o valor deve ser um objeto.")
        if set(registro) != conjunto_campos:
            raise DadosInvalidosError(
                f"Registro {indice}: os campos diferem dos demais. "
                "Todos os registros devem conter os mesmos campos."
            )
        for campo, valor in registro.items():
            if not isinstance(valor, str):
                raise DadosInvalidosError(
                    f"Registro {indice}, campo '{campo}': valores devem ser texto "
                    "para garantir conversão CSV/JSON sem perda de tipos."
                )

    return registros
