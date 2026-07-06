"""
Testes para a edição de mensalidade no Financeiro.

Cobrem a lógica de banco usada pelo EditarMensalidadeDialog:
- a query com COALESCE/LEFT JOIN que funciona tanto para adultos
  (aluno_id positivo) quanto para kids (aluno_id negativo);
- a atualização que altera SOMENTE o plano (que ajusta o valor) e o
  status do pagamento.
"""
import pytest

from database import db
from database.db import get_conn, _extrair_valor_plano
from database import kids_db


def _inserir_mensalidade(aluno_id, valor, status="PENDENTE"):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO mensalidades (aluno_id, valor, data_vencimento, status, observacoes)
        VALUES (?, ?, '2025-01-10', ?, 'teste')
        """,
        (aluno_id, valor, status),
    )
    mid = cur.lastrowid
    conn.commit()
    conn.close()
    return mid


def _query_editar(mensalidade_id):
    """Reproduz a query usada por editar_mensalidade()."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT m.id, m.aluno_id, m.valor, m.data_vencimento, m.data_pagamento,
               m.status, m.observacoes, m.criado_em,
               COALESCE(a.nome, k.nome)  AS nome,
               COALESCE(a.plano, k.plano) AS plano
        FROM mensalidades m
        LEFT JOIN alunos a ON m.aluno_id = a.id
        LEFT JOIN kids   k ON m.aluno_id = -k.id
        WHERE m.id=?
        """,
        (mensalidade_id,),
    )
    dados = cur.fetchone()
    conn.close()
    return dados


def _salvar(dados, plano_texto, status):
    """Reproduz a lógica de salvar_alteracoes() (apenas plano + status)."""
    from datetime import date

    mensalidade_id = dados[0]
    aluno_id = dados[1]
    valor = _extrair_valor_plano(plano_texto)

    conn = get_conn()
    cur = conn.cursor()

    if aluno_id is not None and aluno_id >= 0:
        cur.execute("UPDATE alunos SET plano=? WHERE id=?", (plano_texto, aluno_id))
    elif aluno_id is not None:
        cur.execute("UPDATE kids SET plano=? WHERE id=?", (plano_texto, -aluno_id))

    campos = ["status=?"]
    params = [status]
    if valor is not None:
        campos.append("valor=?")
        params.append(valor)
    if status == "PAGO":
        campos.append("data_pagamento=?")
        params.append(date.today().isoformat())
    else:
        campos.append("data_pagamento=?")
        params.append(None)
    params.append(mensalidade_id)
    cur.execute(f"UPDATE mensalidades SET {', '.join(campos)} WHERE id=?", params)
    conn.commit()
    conn.close()


class TestQueryEditarMensalidade:
    def test_query_retorna_dados_de_adulto(self, temp_db):
        aluno_id = db.inserir_aluno(
            "Carlos Adulto", "11122233344", "c@x.com", "11999999999",
            "01000000", "Rua A", "1990-01-01", "Azul", "2", "80", "1.80",
            "Adulto - R$180", None, None, None,
        )
        mid = _inserir_mensalidade(aluno_id, 180.0)

        dados = _query_editar(mid)

        assert dados is not None
        assert dados[8] == "Carlos Adulto"      # nome
        assert dados[9] == "Adulto - R$180"     # plano

    def test_query_retorna_dados_de_kid(self, temp_db):
        kid_id = kids_db.inserir_kid(
            "Pedrinho Kid", "", "Carlos Resp", "11122233344", "k@x.com",
            "11888888888", "01000000", "Rua B", "2016-01-01", "Cinza",
            "1", "30", "1.20", "Kids (5-13) - R$150", None, None,
        )
        # a inserção do kid já gera a mensalidade automaticamente (id negativo)
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id FROM mensalidades WHERE aluno_id=?", (-kid_id,))
        mid = cur.fetchone()[0]
        conn.close()

        dados = _query_editar(mid)

        assert dados is not None
        assert dados[1] == -kid_id               # aluno_id negativo
        assert dados[8] == "Pedrinho Kid"        # nome vindo da tabela kids
        assert dados[9] == "Kids (5-13) - R$150"  # plano


class TestSalvarEdicaoMensalidade:
    def test_altera_plano_e_valor_do_adulto(self, temp_db):
        aluno_id = db.inserir_aluno(
            "Carlos Adulto", "11122233344", "c@x.com", "11999999999",
            "01000000", "Rua A", "1990-01-01", "Azul", "2", "80", "1.80",
            "Adulto - R$180", None, None, None,
        )
        mid = _inserir_mensalidade(aluno_id, 180.0)
        dados = _query_editar(mid)

        _salvar(dados, "Adulto - R$220", "PENDENTE")

        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT plano FROM alunos WHERE id=?", (aluno_id,))
        assert cur.fetchone()[0] == "Adulto - R$220"
        cur.execute("SELECT valor, status, data_pagamento FROM mensalidades WHERE id=?", (mid,))
        valor, status, data_pag = cur.fetchone()
        conn.close()
        assert valor == 220.0
        assert status == "PENDENTE"
        assert data_pag is None

    def test_marcar_pago_define_data_pagamento(self, temp_db):
        aluno_id = db.inserir_aluno(
            "Carlos Adulto", "11122233344", "c@x.com", "11999999999",
            "01000000", "Rua A", "1990-01-01", "Azul", "2", "80", "1.80",
            "Adulto - R$180", None, None, None,
        )
        mid = _inserir_mensalidade(aluno_id, 180.0)
        dados = _query_editar(mid)

        _salvar(dados, "Adulto - R$180", "PAGO")

        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT status, data_pagamento FROM mensalidades WHERE id=?", (mid,))
        status, data_pag = cur.fetchone()
        conn.close()
        assert status == "PAGO"
        assert data_pag is not None

    def test_altera_plano_e_status_do_kid(self, temp_db):
        kid_id = kids_db.inserir_kid(
            "Pedrinho Kid", "", "Carlos Resp", "11122233344", "k@x.com",
            "11888888888", "01000000", "Rua B", "2016-01-01", "Cinza",
            "1", "30", "1.20", "Kids (5-13) - R$150", None, None,
        )
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id FROM mensalidades WHERE aluno_id=?", (-kid_id,))
        mid = cur.fetchone()[0]
        conn.close()
        dados = _query_editar(mid)

        _salvar(dados, "Kids (5-13) - R$170", "PAGO")

        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT plano FROM kids WHERE id=?", (kid_id,))
        assert cur.fetchone()[0] == "Kids (5-13) - R$170"
        cur.execute("SELECT valor, status FROM mensalidades WHERE id=?", (mid,))
        valor, status = cur.fetchone()
        conn.close()
        assert valor == 170.0
        assert status == "PAGO"
