"""Teste do filtro de dependentes no Dashboard."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication


def _app():
    return QApplication.instance() or QApplication([])


class TestDashboardFiltroDependentes:
    def test_get_filtered(self, temp_db):
        _app()
        from ui.dashboard_tab import DashboardTab
        d = DashboardTab()
        d.metricas = {
            "all_students_list": [
                {"nome": "Adulto Titular", "tipo": "adultos"},
                {"nome": "Adulto Dep", "tipo": "dependentes"},
                {"nome": "Kid Dep", "tipo": "kids", "plano": "Dependente"},
                {"nome": "Kid Normal", "tipo": "kids", "plano": "Kids (5-13) - R$150"},
            ]
        }

        d._filter = "dependentes"
        assert {s["nome"] for s in d._get_filtered()} == {"Adulto Dep", "Kid Dep"}

        d._filter = "kids"
        assert {s["nome"] for s in d._get_filtered()} == {"Kid Dep", "Kid Normal"}

        d._filter = "adultos"
        assert {s["nome"] for s in d._get_filtered()} == {"Adulto Titular"}

        d._filter = "todos"
        assert len(d._get_filtered()) == 4
