"""
Testes para os filtros da aba de Gestão Financeira:
- filtro por tipo (Adulto/Kids)
- busca por nome
- combinação com o filtro por mês
"""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from ui.financeiro_tab import FinanceiroTab


def _m(id_, nome, mes, tipo):
    """Cria uma tupla no formato de listar_mensalidades().

    [0]id [1]nome [2]valor [3]data_vencimento [4]data_pagamento
    [5]status [6]obs [7]foto [8]plano [9]tipo_aluno
    """
    return (
        id_, nome, 180.0, f"2025-{mes:02d}-10", None,
        "PENDENTE", "", None, "Plano", tipo,
    )


DADOS = [
    _m(1, "Carlos Silva", 1, "adulto"),
    _m(2, "Ana Souza", 1, "adulto"),
    _m(3, "Pedrinho Silva", 1, "kid"),
    _m(4, "Joana Kid", 2, "kid"),          # mês diferente
    _m(5, "Carlos Adulto Fev", 2, "adulto"),  # mês diferente
]


class TestFiltrarMensalidades:
    def test_apenas_mes_sem_outros_filtros(self):
        res = FinanceiroTab.filtrar_mensalidades(DADOS, mes=1)
        ids = {m[0] for m in res}
        assert ids == {1, 2, 3}

    def test_filtro_tipo_adulto(self):
        res = FinanceiroTab.filtrar_mensalidades(DADOS, mes=1, tipo="Adulto")
        ids = {m[0] for m in res}
        assert ids == {1, 2}

    def test_filtro_tipo_kids(self):
        res = FinanceiroTab.filtrar_mensalidades(DADOS, mes=1, tipo="Kids")
        ids = {m[0] for m in res}
        assert ids == {3}

    def test_busca_por_nome_case_insensitive(self):
        res = FinanceiroTab.filtrar_mensalidades(DADOS, mes=1, termo="silva")
        ids = {m[0] for m in res}
        assert ids == {1, 3}

    def test_busca_por_nome_parcial(self):
        res = FinanceiroTab.filtrar_mensalidades(DADOS, mes=1, termo="carlos")
        ids = {m[0] for m in res}
        assert ids == {1}

    def test_tipo_e_nome_combinados(self):
        res = FinanceiroTab.filtrar_mensalidades(DADOS, mes=1, tipo="Adulto", termo="silva")
        ids = {m[0] for m in res}
        assert ids == {1}

    def test_termo_com_espacos_em_branco(self):
        res = FinanceiroTab.filtrar_mensalidades(DADOS, mes=1, termo="  ana  ")
        ids = {m[0] for m in res}
        assert ids == {2}

    def test_nenhum_resultado(self):
        res = FinanceiroTab.filtrar_mensalidades(DADOS, mes=1, termo="inexistente")
        assert res == []

    def test_ignora_mensalidade_sem_data(self):
        dados = DADOS + [(99, "Sem Data", 180.0, "", None, "PENDENTE", "", None, "Plano", "adulto")]
        res = FinanceiroTab.filtrar_mensalidades(dados, mes=1)
        assert all(m[0] != 99 for m in res)
