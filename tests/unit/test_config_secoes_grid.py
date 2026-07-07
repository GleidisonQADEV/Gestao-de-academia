"""
Testes de UI para a aba de Configurações:
- as seções (Segurança, Planos, Dados, Sistema) ficam lado a lado (grade 2x2);
- os cards de planos continuam empilhados em coluna única.
"""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import QApplication, QGridLayout, QVBoxLayout

from ui.config_tab import ConfigTab


@pytest.fixture(autouse=True)
def _app():
    app = QApplication.instance() or QApplication([])
    yield app


class TestConfigSecoesGrid:
    def test_secoes_em_grade(self, temp_db):
        config = ConfigTab()
        assert isinstance(config.secoes_layout, QGridLayout)

    def test_quatro_secoes_lado_a_lado(self, temp_db):
        config = ConfigTab()
        grid = config.secoes_layout

        posicoes = []
        for idx in range(grid.count()):
            if grid.itemAt(idx).widget() is not None:
                r, c, _rs, _cs = grid.getItemPosition(idx)
                posicoes.append((r, c))

        # 4 seções distribuídas em 2 colunas e 2 linhas
        assert len(posicoes) == 4
        assert {c for _r, c in posicoes} == {0, 1}
        assert {r for r, _c in posicoes} == {0, 1}
        # A primeira linha deve ter duas seções (colunas 0 e 1)
        assert sorted(c for r, c in posicoes if r == 0) == [0, 1]

    def test_planos_em_coluna_unica(self, temp_db):
        config = ConfigTab()
        # Os cards de planos permanecem empilhados verticalmente
        assert isinstance(config.cards_layout, QVBoxLayout)
