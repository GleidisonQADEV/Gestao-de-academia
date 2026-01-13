from datetime import date
from database.db import connect


class FinanceiroService:

    @staticmethod
    def gerar_mensalidades():
        hoje = date.today()
        mes = hoje.month
        ano = hoje.year

        conn = connect()
        cur = conn.cursor()

        cur.execute("SELECT id, valor_mensalidade, dia_vencimento FROM alunos WHERE status='ATIVO'")
        alunos = cur.fetchall()

        for aluno_id, valor, dia in alunos:
            venc = date(ano, mes, min(dia, 28))

            cur.execute("""
                SELECT id FROM mensalidades
                WHERE aluno_id=? 
                AND strftime('%m', data_vencimento)=? 
                AND strftime('%Y', data_vencimento)=?
            """, (aluno_id, f"{mes:02}", str(ano)))

            if cur.fetchone():
                continue

            cur.execute(
                "INSERT INTO mensalidades (aluno_id, valor, data_vencimento, status) VALUES (?, ?, ?, ?)",
                (aluno_id, valor, venc.isoformat(), "PENDENTE")
            )

        conn.commit()
        conn.close()

    @staticmethod
    def marcar_pago(mensal_id):
        hoje = date.today().isoformat()
        conn = connect()
        cur = conn.cursor()
        cur.execute(
            "UPDATE mensalidades SET status='PAGO', data_pagamento=? WHERE id=?",
            (hoje, mensal_id)
        )
        conn.commit()
        conn.close()
