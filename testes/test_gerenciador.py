"""Cenários reais + falhas, com unittest da biblioteca padrão."""

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from gerenciador.backup import criar_backup
from gerenciador.conversao import converter
from gerenciador.excecoes import DadosInvalidosError
from gerenciador.persistencia import atualizar_registro, ler_registros, salvar_registros
from main import executar


class GerenciadorTests(unittest.TestCase):
    def setUp(self):
        self.diretorio = tempfile.TemporaryDirectory()
        self.addCleanup(self.diretorio.cleanup)
        self.pasta = Path(self.diretorio.name)
        self.csv = self.pasta / "origem.csv"
        self.json = self.pasta / "origem.json"
        self.dados = [
            {"id": "001", "nome": "João, Júnior", "obs": "Linha 1\nLinha 2", "codigo": "0005"},
            {"id": "002", "nome": 'Ana "Silva"', "obs": "ação & revisão", "codigo": "0000"},
        ]
        salvar_registros(self.csv, self.dados)
        salvar_registros(self.json, self.dados)

    def test_01_ler_csv(self):
        self.assertEqual(ler_registros(self.csv), self.dados)

    def test_02_ler_json(self):
        self.assertEqual(ler_registros(self.json), self.dados)

    def test_03_converter_csv_json_sem_perda(self):
        destino = self.pasta / "convertido.json"
        quantidade, backup = converter(self.csv, destino)
        self.assertEqual(quantidade, 2)
        self.assertIsNone(backup)
        self.assertEqual(ler_registros(destino), self.dados)

    def test_04_converter_json_csv_sem_perda(self):
        destino = self.pasta / "convertido.csv"
        quantidade, backup = converter(self.json, destino)
        self.assertEqual(quantidade, 2)
        self.assertIsNone(backup)
        self.assertEqual(ler_registros(destino), self.dados)

    def test_05_csv_json_csv_ida_e_volta(self):
        meio = self.pasta / "intermediario.json"
        final = self.pasta / "final.csv"
        converter(self.csv, meio)
        converter(meio, final)
        self.assertEqual(ler_registros(final), self.dados)

    def test_06_backup_antes_de_sobrescrever(self):
        original = self.json.read_bytes()
        destino = self.pasta / "origem.json"
        converter(self.csv, destino)
        copias = list((self.pasta / "backups").glob("origem.json.*.bak"))
        self.assertEqual(len(copias), 1)
        self.assertEqual(copias[0].read_bytes(), original)

    def test_07_atualizar_csv_preserva_valores_anteriores_no_backup(self):
        antes = self.csv.read_bytes()
        alterou, copia = atualizar_registro(self.csv, "002", "nome", "Beatriz")
        self.assertTrue(alterou)
        self.assertIsNotNone(copia)
        self.assertEqual(copia.read_bytes(), antes)
        self.assertEqual(ler_registros(self.csv)[1]["nome"], "Beatriz")
        self.assertEqual(ler_registros(self.csv)[0], self.dados[0])

    def test_08_atualizar_json(self):
        alterou, copia = atualizar_registro(self.json, "001", "obs", "Atualizado")
        self.assertTrue(alterou)
        self.assertTrue(copia.is_file())
        self.assertEqual(ler_registros(self.json)[0]["obs"], "Atualizado")

    def test_09_valor_igual_sem_backup(self):
        alterou, copia = atualizar_registro(self.csv, "001", "codigo", "0005")
        self.assertFalse(alterou)
        self.assertIsNone(copia)
        self.assertFalse((self.pasta / "backups").exists())

    def test_10_erro_arquivo_inexistente(self):
        with self.assertRaises(FileNotFoundError):
            ler_registros(self.pasta / "naoexiste.csv")
        self.assertEqual(executar(["ler", str(self.pasta / "naoexiste.csv")]), 1)

    def test_11_erro_utf8(self):
        invalido = self.pasta / "invalido.csv"
        with open(invalido, "wb") as arquivo:
            arquivo.write(b"id,nome\n001,\xff\n")
        with self.assertRaises(UnicodeDecodeError):
            ler_registros(invalido)

    def test_12_erro_json_malformado(self):
        invalido = self.pasta / "invalido.json"
        with open(invalido, "w", encoding="utf-8") as arquivo:
            arquivo.write('[{"id": "001"},')
        with self.assertRaises(json.JSONDecodeError):
            ler_registros(invalido)

    def test_13_csv_campos_inconsistentes(self):
        invalido = self.pasta / "invalido.csv"
        with open(invalido, "w", encoding="utf-8", newline="") as arquivo:
            arquivo.write("id,nome\n001\n")
        with self.assertRaises(DadosInvalidosError):
            ler_registros(invalido)

    def test_14_json_tipos_nao_textuais_recusados(self):
        invalido = self.pasta / "invalido.json"
        with open(invalido, "w", encoding="utf-8") as arquivo:
            json.dump([{"id": 1, "nome": "Ana"}], arquivo)
        with self.assertRaises(DadosInvalidosError):
            ler_registros(invalido)

    def test_15_falha_no_backup_impede_modificacao(self):
        conteudo_original = self.csv.read_bytes()
        with patch("gerenciador.persistencia.criar_backup", side_effect=PermissionError("bloqueado")):
            with self.assertRaises(PermissionError):
                atualizar_registro(self.csv, "001", "nome", "Novo nome")
        self.assertEqual(self.csv.read_bytes(), conteudo_original)

    def test_16_falha_na_troca_preserva_destino(self):
        original = self.json.read_bytes()
        with patch("gerenciador.persistencia.os.replace", side_effect=OSError("erro simulado")):
            with self.assertRaises(OSError):
                salvar_registros(self.json, self.dados)
        self.assertEqual(self.json.read_bytes(), original)
        self.assertEqual(len(list(self.pasta.glob(".*.tmp"))), 0)

    def test_17_chave_json_duplicada_rejeitada(self):
        invalido = self.pasta / "duplicado.json"
        with open(invalido, "w", encoding="utf-8") as arquivo:
            arquivo.write('[{"id":"001","id":"002"}]')
        with self.assertRaises(DadosInvalidosError):
            ler_registros(invalido)

    def test_18_id_duplicado_rejeita_atualizacao(self):
        repetidos = [dict(self.dados[0]), dict(self.dados[0])]
        salvar_registros(self.csv, repetidos)
        with self.assertRaises(DadosInvalidosError):
            atualizar_registro(self.csv, "001", "nome", "Teste")


if __name__ == "__main__":
    unittest.main()
