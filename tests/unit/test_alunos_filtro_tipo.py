"""Testes para o filtro por tipo (Todos/Adulto/Dependente/Kids) na aba Alunos."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import database.db as db
import database.kids_db as kids_db
from PySide6.QtWidgets import QApplication


def _app():
    return QApplication.instance() or QApplication([])


def _nomes_visiveis(tab):
    return [w._dados["nome"] for w in tab._linhas_tabela()]


class TestFiltroTipo:
    def test_filtros_por_tipo(self, temp_db):
        _app()
        # Responsável (adulto titular)
        resp = db.inserir_aluno(
            "Resp Titular", "11111111111", "e", "119", "01", "R", "1990-01-01",
            "Azul", "1", "80", "1.8", "Adulto - R$180", None, None
        )
        # Adulto dependente (vinculado a um responsável)
        dep = db.inserir_aluno(
            "Dep Adulto", "22222222222", "e", "119", "01", "R", "1990-01-01",
            "Branca", "0", "80", "1.8", "Vinculado ao responsável", None, None
        )
        conn = db.get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE alunos SET responsavel_id=? WHERE id=?", (resp, dep))
        conn.commit()
        conn.close()
        # Kid dependente (plano Dependente) e kid normal
        kids_db.inserir_kid(
            "Kid Dep", None, "Resp Titular", "11111111111", "e", "119", "01", "R",
            "2015-01-01", "Amarela", "0", "30", "1.3", "Dependente", None, None
        )
        kids_db.inserir_kid(
            "Kid Normal", None, "Outro Resp", "99999999999", "e", "119", "01", "R",
            "2015-01-01", "Branca", "0", "30", "1.3", "Kids (5-13) - R$150", None, None
        )

        from ui.alunos_tab import AlunosTab
        tab = AlunosTab()

        tab.combo_tipo.setCurrentText("Adulto")
        tab.buscar()
        nomes = _nomes_visiveis(tab)
        assert "Resp Titular" in nomes
        assert "Dep Adulto" not in nomes
        assert "Kid Dep" not in nomes and "Kid Normal" not in nomes

        tab.combo_tipo.setCurrentText("Kids")
        tab.buscar()
        nomes = _nomes_visiveis(tab)
        assert {"Kid Dep", "Kid Normal"}.issubset(set(nomes))
        assert "Resp Titular" not in nomes and "Dep Adulto" not in nomes

        tab.combo_tipo.setCurrentText("Dependente")
        tab.buscar()
        nomes = _nomes_visiveis(tab)
        assert "Dep Adulto" in nomes
        assert "Kid Dep" in nomes
        assert "Resp Titular" not in nomes
        assert "Kid Normal" not in nomes

        tab.combo_tipo.setCurrentText("Todos")
        tab.buscar()
        nomes = _nomes_visiveis(tab)
        assert {"Resp Titular", "Dep Adulto", "Kid Dep", "Kid Normal"}.issubset(set(nomes))
