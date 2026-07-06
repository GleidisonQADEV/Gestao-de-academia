"""
Testes para exclusão de alunos e tratamento de dependentes:
- ao excluir aluno/kid, suas mensalidades são removidas;
- obter_dependentes retorna dependentes adultos (responsavel_id) e kids (resp_cpf);
- reatribuir_dependentes transfere os dependentes para um novo responsável;
- desvincular_dependentes remove o vínculo dos dependentes adultos.
"""
from database import db
from database.db import (
    get_conn, excluir_aluno, obter_dependentes,
    reatribuir_dependentes, desvincular_dependentes,
)
from database import kids_db
from database.kids_db import excluir_kid


def _novo_adulto(nome, cpf, plano="Adulto - R$180"):
    return db.inserir_aluno(
        nome, cpf, f"{cpf}@x.com", "11999999999", "01000000", "Rua A",
        "1990-01-01", "Branca", "1", "80", "1.80", plano, None, None, None,
    )


def _inserir_mensalidade(aluno_id, valor=180.0):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO mensalidades (aluno_id, valor, data_vencimento, status, observacoes)
           VALUES (?, ?, '2025-01-10', 'PENDENTE', 'teste')""",
        (aluno_id, valor),
    )
    conn.commit()
    conn.close()


def _contar_mensalidades(aluno_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM mensalidades WHERE aluno_id=?", (aluno_id,))
    n = cur.fetchone()[0]
    conn.close()
    return n


class TestExclusaoRemoveMensalidades:
    def test_excluir_adulto_remove_mensalidades(self, temp_db):
        aluno_id = _novo_adulto("Carlos", "11122233344")
        _inserir_mensalidade(aluno_id)
        _inserir_mensalidade(aluno_id)
        assert _contar_mensalidades(aluno_id) == 2

        excluir_aluno(aluno_id)

        assert _contar_mensalidades(aluno_id) == 0
        conn = get_conn(); cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM alunos WHERE id=?", (aluno_id,))
        assert cur.fetchone()[0] == 0
        conn.close()

    def test_excluir_kid_remove_mensalidades(self, temp_db):
        kid_id = kids_db.inserir_kid(
            "Pedrinho", "", "Resp", "55566677788", "k@x.com", "11888888888",
            "01000000", "Rua B", "2016-01-01", "Branca", "1", "30", "1.20",
            "Kids (5-13) - R$150", None, None,
        )
        # inserir_kid já gera 1 mensalidade (aluno_id = -kid_id)
        assert _contar_mensalidades(-kid_id) >= 1

        excluir_kid(kid_id)

        assert _contar_mensalidades(-kid_id) == 0
        conn = get_conn(); cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM kids WHERE id=?", (kid_id,))
        assert cur.fetchone()[0] == 0
        conn.close()


class TestObterDependentes:
    def test_dependentes_adultos_e_kids(self, temp_db):
        resp_id = _novo_adulto("Responsavel", "11122233344")
        dep_adulto = _novo_adulto("Filho Adulto", "99988877766")
        # vincular adulto como dependente
        conn = get_conn(); cur = conn.cursor()
        cur.execute("UPDATE alunos SET responsavel_id=? WHERE id=?", (resp_id, dep_adulto))
        conn.commit(); conn.close()

        kid_id = kids_db.inserir_kid(
            "Filho Kid", "", "Responsavel", "11122233344", "k@x.com",
            "11888888888", "01000000", "Rua B", "2016-01-01", "Branca",
            "1", "30", "1.20", "Vinculado ao responsável", None, None,
        )

        deps = obter_dependentes(resp_id, "11122233344")

        assert [a[0] for a in deps["adultos"]] == [dep_adulto]
        assert [k[0] for k in deps["kids"]] == [kid_id]

    def test_sem_dependentes(self, temp_db):
        resp_id = _novo_adulto("Sozinho", "11122233344")
        deps = obter_dependentes(resp_id, "11122233344")
        assert deps == {"adultos": [], "kids": []}


class TestReatribuirEDesvincular:
    def test_reatribuir_dependentes(self, temp_db):
        antigo = _novo_adulto("Antigo Resp", "11122233344")
        novo = _novo_adulto("Novo Resp", "22233344455")
        dep = _novo_adulto("Dependente", "99988877766")

        conn = get_conn(); cur = conn.cursor()
        cur.execute("UPDATE alunos SET responsavel_id=? WHERE id=?", (antigo, dep))
        conn.commit(); conn.close()

        kid_id = kids_db.inserir_kid(
            "Kid Dep", "", "Antigo Resp", "11122233344", "k@x.com",
            "11888888888", "01000000", "Rua B", "2016-01-01", "Branca",
            "1", "30", "1.20", "Vinculado ao responsável", None, None,
        )

        reatribuir_dependentes(antigo, "11122233344", novo, "Novo Resp", "22233344455")

        conn = get_conn(); cur = conn.cursor()
        cur.execute("SELECT responsavel_id FROM alunos WHERE id=?", (dep,))
        assert cur.fetchone()[0] == novo
        cur.execute("SELECT resp_cpf, resp_nome FROM kids WHERE id=?", (kid_id,))
        cpf, nome = cur.fetchone()
        conn.close()
        assert cpf == "22233344455"
        assert nome == "Novo Resp"

    def test_reatribuir_para_dependente_zera_seu_responsavel(self, temp_db):
        antigo = _novo_adulto("Antigo Resp", "11122233344")
        promovido = _novo_adulto("Promovido", "22233344455")

        conn = get_conn(); cur = conn.cursor()
        cur.execute("UPDATE alunos SET responsavel_id=? WHERE id=?", (antigo, promovido))
        conn.commit(); conn.close()

        reatribuir_dependentes(antigo, "11122233344", promovido, "Promovido", "22233344455")

        conn = get_conn(); cur = conn.cursor()
        cur.execute("SELECT responsavel_id FROM alunos WHERE id=?", (promovido,))
        assert cur.fetchone()[0] is None
        conn.close()

    def test_desvincular_dependentes(self, temp_db):
        resp = _novo_adulto("Resp", "11122233344")
        dep = _novo_adulto("Dep", "99988877766")
        conn = get_conn(); cur = conn.cursor()
        cur.execute("UPDATE alunos SET responsavel_id=? WHERE id=?", (resp, dep))
        conn.commit(); conn.close()

        desvincular_dependentes(resp)

        conn = get_conn(); cur = conn.cursor()
        cur.execute("SELECT responsavel_id FROM alunos WHERE id=?", (dep,))
        assert cur.fetchone()[0] is None
        conn.close()
