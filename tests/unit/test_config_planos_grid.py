"""
Testes de UI para a aba de Configurações:
- os cards de planos são organizados em grade de 2 colunas (lado a lado).
"""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import QApplication, QGridLayout

from database import db
from database import kids_db
from ui.config_tab import ConfigTab, PlanoCard


@pytest.fixture(autouse=True)
def _app():
    app = QApplication.instance() or QApplication([])
    yield app


class TestConfigPlanosGrid:
    def test_cards_layout_e_grade(self, temp_db):
        config = ConfigTab()
        assert isinstance(config.cards_layout, QGridLayout)

    def test_planos_ficam_lado_a_lado(self, temp_db):
        # Garante pelo menos 4 planos cadastrados
        for i in range(4):
            try:
                db.criar_plano(f"Plano Teste {i}", 100.0 + i)
            except Exception:
                pass

        config = ConfigTab()
        config.carregar_planos()

        # Coletar posições (linha, coluna) de cada PlanoCard na grade
        posicoes = []
        for idx in range(config.cards_layout.count()):
            item = config.cards_layout.itemAt(idx)
            w = item.widget()
            if isinstance(w, PlanoCard):
                r, c, _rs, _cs = config.cards_layout.getItemPosition(idx)
                posicoes.append((r, c))

        assert len(posicoes) >= 4
        # Deve haver cards na coluna 0 e na coluna 1 (duas colunas)
        colunas = {c for _r, c in posicoes}
        assert colunas == {0, 1}
        # A primeira linha deve ter dois cards (colunas 0 e 1)
        primeira_linha = [c for r, c in posicoes if r == 0]
        assert sorted(primeira_linha) == [0, 1]
