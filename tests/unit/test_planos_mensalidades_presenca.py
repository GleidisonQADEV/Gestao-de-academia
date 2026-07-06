"""Testes para regras de planos, mensalidades, presença e colunas extras."""
from datetime import date

import database.db as db


class TestExtrairValorPlano:
    def test_valor(self):
        assert db._extrair_valor_plano("Adulto - R$180") == 180.0
        assert db._extrair_valor_plano("Kids (5-13) - R$150") == 150.0

    def test_bolsista(self):
        assert db._extrair_valor_plano("Plano Bolsista (Patrocinado)") == 0.0

    def test_sem_valor(self):
        assert db._extrair_valor_plano("Plano Qualquer") is None
        assert db._extrair_valor_plano("") is None


def _novo_aluno(plano="Adulto - R$180"):
    return db.inserir_aluno(
        "Teste", "11122233344", "e@e", "1199", "01", "Rua", "1990-01-01",
        "Azul", "1", "80", "1.8", plano, None, None
    )


class TestMensalidades:
    def test_nao_gera_meses_passados(self, temp_db):
        aid = _novo_aluno()
        db.gerar_mensalidades_anuais(date.today().year)
        conn = db.get_conn()
        cur = conn.cursor()
        cur.execute(
            "SELECT strftime('%m', data_vencimento) FROM mensalidades WHERE aluno_id=?",
            (aid,),
        )
        meses = [int(m[0]) for m in cur.fetchall()]
        conn.close()
        assert meses, "deveria gerar mensalidades do mês atual em diante"
        assert min(meses) >= date.today().month

    def test_atualizar_mensalidades_por_plano(self, temp_db):
        aid = _novo_aluno("Adulto - R$180")
        db.gerar_mensalidades_anuais(date.today().year)
        atualizadas = db.atualizar_mensalidades_por_plano(aid, "Adulto - R$250")
        assert atualizadas >= 1
        conn = db.get_conn()
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT valor FROM mensalidades WHERE aluno_id=?", (aid,))
        valores = {r[0] for r in cur.fetchall()}
        conn.close()
        assert valores == {250.0}

    def test_definir_plano_e_gerar(self, temp_db):
        # aluno sem plano -> não gera
        aid = _novo_aluno(plano=None)
        assert db.gerar_mensalidades_anuais(date.today().year) == 0
        # define plano -> gera
        db.definir_plano_aluno(aid, "Adulto - R$180", "adulto")
        criadas = db.gerar_mensalidades_anuais(date.today().year)
        assert criadas >= 1
        conn = db.get_conn()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*), MIN(valor) FROM mensalidades WHERE aluno_id=?", (aid,))
        qtd, valor = cur.fetchone()
        conn.close()
        assert qtd >= 1 and valor == 180.0

    def test_definir_plano_dependente_remove_pendentes(self, temp_db):
        aid = _novo_aluno("Adulto - R$180")
        db.gerar_mensalidades_anuais(date.today().year)
        # aplicar plano nao faturavel ('Dependente') remove as pendentes
        db.definir_plano_aluno(aid, "Dependente", "adulto")
        conn = db.get_conn()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM mensalidades WHERE aluno_id=? AND status='PENDENTE'", (aid,))
        assert cur.fetchone()[0] == 0
        conn.close()


class TestPresenca:
    def test_percentual_sem_registros(self, temp_db):
        aid = _novo_aluno()
        pct, pres = db.obter_percentual_presenca(aid, "adulto")
        assert pct == 0.0 and pres == 0

    def test_percentual_com_registros(self, temp_db):
        aid = _novo_aluno()
        hoje = date.today()
        conn = db.get_conn()
        cur = conn.cursor()
        for i in range(11):
            cur.execute(
                "INSERT INTO registros_presenca (aluno_id, data_registro, hora_entrada, tipo_aluno)"
                " VALUES (?, ?, ?, 'adulto')",
                (aid, hoje.isoformat(), f"08:{i:02d}:00"),
            )
        conn.commit()
        conn.close()
        pct, pres = db.obter_percentual_presenca(aid, "adulto", hoje.year, hoje.month)
        assert pres == 11
        assert pct == round(11 / db.AULAS_POR_MES * 100, 1)

    def test_frequencia_media(self, temp_db):
        _novo_aluno()
        media, total_alunos, total_pres = db.obter_frequencia_media_mes()
        assert total_alunos >= 1
        assert media == 0.0  # sem presenças


class TestColunasExtras:
    def test_colunas_existem_e_persistem(self, temp_db):
        aid = db.inserir_aluno(
            "Com Ficha", "55566677788", "e@e", "1199", "01", "Rua", "1990-01-01",
            "Azul", "1", "80", "1.8", "Adulto - R$180", None, None,
            tipo_sanguineo="O+", contato_emergencia="Maria 123",
            alergias="Nenhuma", condicoes_medicas="Hipertensão", tempo_faixa="2 anos",
        )
        conn = db.get_conn()
        cur = conn.cursor()
        cur.execute(
            "SELECT tipo_sanguineo, contato_emergencia, alergias, condicoes_medicas, tempo_faixa"
            " FROM alunos WHERE id=?",
            (aid,),
        )
        row = cur.fetchone()
        conn.close()
        assert row == ("O+", "Maria 123", "Nenhuma", "Hipertensão", "2 anos")

    def test_atualizar_preserva_extras(self, temp_db):
        aid = db.inserir_aluno(
            "Preserva", "11100022233", "e@e", "1199", "01", "Rua", "1990-01-01",
            "Azul", "1", "80", "1.8", "Adulto - R$180", None, None,
            tipo_sanguineo="AB+", tempo_faixa="3 anos",
        )
        # edição sem informar os extras (como faz o diálogo atual)
        db.atualizar_aluno(
            aid, "Preserva Editado", "11100022233", "e@e", "1199", "01", "Rua",
            "1990-01-01", "Roxa", "2", "80", "1.8", "Adulto - R$180", None, None, None,
        )
        conn = db.get_conn()
        cur = conn.cursor()
        cur.execute("SELECT nome, faixa, tipo_sanguineo, tempo_faixa FROM alunos WHERE id=?", (aid,))
        row = cur.fetchone()
        conn.close()
        assert row == ("Preserva Editado", "Roxa", "AB+", "3 anos")
