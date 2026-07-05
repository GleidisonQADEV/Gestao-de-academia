"""Testes para as cores das faixas na aba de alunos."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from ui.alunos_tab import cor_faixa


class TestCorFaixa:
    def test_kids_amarela_variantes(self):
        assert cor_faixa("Amarela") == "#f2c200"
        assert cor_faixa("Amarela c/b") == "#f2c200"
        assert cor_faixa("Amarela com branco") == "#f2c200"

    def test_kids_demais(self):
        assert cor_faixa("Laranja c/p") == "#e67e22"
        assert cor_faixa("Verde") == "#2e9e4f"
        assert cor_faixa("Cinza c/b") == "#8a8a8a"

    def test_adulto(self):
        assert cor_faixa("Branca") == "#d0d0d0"
        assert cor_faixa("Azul") == "#1a4fa0"
        assert cor_faixa("Roxa") == "#6b2fa0"
        assert cor_faixa("Marrom") == "#8b4a1f"
        assert cor_faixa("Preta") == "#111111"

    def test_desconhecida(self):
        assert cor_faixa("") == "#888888"
        assert cor_faixa("Inexistente") == "#888888"
