"""Testes para geração dos relatórios em PDF."""
import os
import tempfile
from datetime import date

import database.db as db
from utils import pdf_report


def _aluno():
    return db.inserir_aluno(
        "Aluno PDF", "11122233344", "e@e", "1199", "01", "Rua", "1990-01-01",
        "Azul", "1", "80", "1.8", "Adulto - R$180", None, None
    )


def _pdf_valido(caminho):
    return os.path.exists(caminho) and os.path.getsize(caminho) > 500


class TestPdfReport:
    def test_relatorio_financeiro(self, temp_db):
        _aluno()
        db.gerar_mensalidades_anuais(date.today().year)
        caminho = tempfile.mktemp(suffix=".pdf")
        pdf_report.gerar_relatorio_financeiro(date.today().year, date.today().month, caminho)
        assert _pdf_valido(caminho)
        os.unlink(caminho)

    def test_lista_alunos(self, temp_db):
        _aluno()
        caminho = tempfile.mktemp(suffix=".pdf")
        pdf_report.gerar_lista_alunos(caminho)
        assert _pdf_valido(caminho)
        os.unlink(caminho)

    def test_relatorio_frequencia(self, temp_db):
        _aluno()
        caminho = tempfile.mktemp(suffix=".pdf")
        pdf_report.gerar_relatorio_frequencia(caminho)
        assert _pdf_valido(caminho)
        os.unlink(caminho)

    def test_ficha_aluno(self, temp_db):
        aid = _aluno()
        caminho = tempfile.mktemp(suffix=".pdf")
        pdf_report.gerar_ficha_aluno(aid, caminho)
        assert _pdf_valido(caminho)
        os.unlink(caminho)

    def test_ficha_aluno_inexistente(self, temp_db):
        import pytest
        with pytest.raises(ValueError):
            pdf_report.gerar_ficha_aluno(999999, tempfile.mktemp(suffix=".pdf"))
