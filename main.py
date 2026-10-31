"""Interface de linha de comando do Gerenciador de Persistência CSV/JSON.

Exemplos:
    python main.py ler dados/clientes.csv
    python main.py converter dados/clientes.csv resultados/clientes_convertidos.json
    python main.py atualizar dados/clientes.csv --id 002 --campo cidade --valor 'Balsas - MA'
"""

import argparse
import csv
import json
import sys

from gerenciador import atualizar_registro, converter, ler_registros
from gerenciador.excecoes import DadosInvalidosError


def criar_analisador() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Gerenciador seguro de arquivos CSV e JSON (TED 03)."
    )
    comandos = parser.add_subparsers(dest="comando", required=True)
    ler = comandos.add_parser("ler", help="Lê e mostra os registros do arquivo.")
    ler.add_argument("arquivo", help="Caminho do arquivo .csv ou .json.")

    conversor = comandos.add_parser("converter", help="Converte CSV em JSON ou vice-versa.")
    conversor.add_argument("origem")
    conversor.add_argument("destino")

    atualizar = comandos.add_parser("atualizar", help="Altera um campo pelo identificador id.")
    atualizar.add_argument("arquivo")
    atualizar.add_argument("--id", dest="identificador", required=True)
    atualizar.add_argument("--campo", required=True)
    atualizar.add_argument("--valor", required=True)
    return parser


def executar(argumentos: list[str] | None = None) -> int:
    args = criar_analisador().parse_args(argumentos)
    try:
        if args.comando == "ler":
            registros = ler_registros(args.arquivo)
            print(f"[OK] Leitura concluída: {len(registros)} registro(s).")
            print(json.dumps(registros, indent=2, ensure_ascii=False))
        elif args.comando == "converter":
            quantidade, backup = converter(args.origem, args.destino)
            print(f"[OK] Conversão concluída: {quantidade} registro(s).")
            print(f"[ARQUIVO] {args.destino}")
            if backup:
                print(f"[BACKUP] Cópia anterior preservada em: {backup}")
            else:
                print("[BACKUP] Novo arquivo: não existiam dados anteriores para copiar.")
        elif args.comando == "atualizar":
            alterou, backup = atualizar_registro(
                args.arquivo, args.identificador, args.campo, args.valor
            )
            if alterou:
                print(f"[OK] Registro {args.identificador} atualizado: {args.campo} = {args.valor}")
                print(f"[BACKUP] Cópia anterior preservada em: {backup}")
            else:
                print("[INFO] Valor idêntico ao atual: nenhuma gravação ou backup necessário.")
        return 0
    except FileNotFoundError as exc:
        print(f"[ERRO] Arquivo ou diretório não encontrado: {exc}", file=sys.stderr)
    except PermissionError as exc:
        print(f"[ERRO] Permissão negada ao acessar ou gravar arquivo: {exc}", file=sys.stderr)
    except UnicodeError as exc:
        print(f"[ERRO] Falha de codificação. Utilize UTF-8: {exc}", file=sys.stderr)
    except json.JSONDecodeError as exc:
        print(f"[ERRO] JSON malformado (linha {exc.lineno}, coluna {exc.colno}): {exc.msg}", file=sys.stderr)
    except (DadosInvalidosError, csv.Error) as exc:
        print(f"[ERRO] Dados inválidos: {exc}", file=sys.stderr)
    except OSError as exc:
        print(f"[ERRO] Falha de entrada/saída. Os dados anteriores foram preservados, se existiam: {exc}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(executar())
