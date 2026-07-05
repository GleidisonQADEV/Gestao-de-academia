"""Testes para importação de Kids (menores) com vinculação ao responsável."""
import database.db as db
from utils import sheets_import as si


class TestCabecalhoKid:
    def _c(self, texto):
        return si._campo_do_cabecalho_kid(si._normalizar(texto))

    def test_mapeamento(self):
        assert self._c("Nome completo do aluno") == "nome"
        assert self._c("CPF do aluno") == "cpf"
        assert self._c("Data de nascimento") == "data_nasc"
        assert self._c("Faixa") == "faixa"
        assert self._c("Nome completo do responsável legal") == "resp_nome"
        assert self._c("CPF do responsável legal") == "resp_cpf"
        assert self._c("Telefone (WhatsApp) do responsável") == "telefone"
        assert self._c("E-mail do responsável") == "email"


class TestNormFaixaKid:
    def test_variantes(self):
        assert si._norm_faixa_kid("Amarela com branco") == "Amarela c/b"
        assert si._norm_faixa_kid("Cinza com ponta preta") == "Cinza c/p"
        assert si._norm_faixa_kid("Azul") == "Azul"
        assert si._norm_faixa_kid("branca") == "Branca"
        assert si._norm_faixa_kid("") == "Branca"


class TestImportacaoKids:
    def test_importa_e_vincula(self, temp_db, monkeypatch):
        # Responsável cadastrado como adulto
        db.inserir_aluno(
            "Fernanda Demarchi", "00484892045", "f@f", "119", "01", "R",
            "1985-06-04", "Branca", "1", "60", "1.6", "Adulto - R$180", None, None
        )
        csv = "\n".join([
            "Nome completo do aluno,CPF do aluno,Data de nascimento,Faixa,"
            "Nome completo do responsável legal,CPF do responsável legal,"
            "Telefone (WhatsApp) do responsável,E-mail do responsável,Endereço completo",
            # kid vinculado (resp é aluno)
            "camilla demarchi,85521094091,16/02/2010,Azul,fernanda demarchi,00484892045,48 999,f@f,Rua 1",
            # kid sem responsável cadastrado
            "luiza zago,,22/03/2017,Amarela com branco,Tulio Rodrigues,36565274827,48 888,t@t,Rua 2",
        ])
        monkeypatch.setattr(si, "_baixar_csv_robusto", lambda url: csv)

        resumo = si.importar_kids_de_url("x", plano_padrao="Kids (5-13) - R$150")
        assert resumo["importados"] == 2
        assert resumo["vinculados"] == 1
        assert resumo["erros"] == []

        import database.kids_db as kids_db
        conn = kids_db.get_conn()
        cur = conn.cursor()
        cur.execute("SELECT nome, faixa, resp_nome, resp_cpf, data_nascimento FROM kids ORDER BY nome")
        rows = cur.fetchall()
        conn.close()
        # Camilla vinculada -> resp_nome oficial "Fernanda Demarchi"
        camilla = next(r for r in rows if r[0].startswith("Camilla"))
        assert camilla[2] == "Fernanda Demarchi"
        assert camilla[3] == "00484892045"
        assert camilla[4] == "2010-02-16"
        luiza = next(r for r in rows if r[0].startswith("Luiza"))
        assert luiza[1] == "Amarela c/b"

    def test_kids_sem_cpf_nao_colidem(self, temp_db, monkeypatch):
        csv = "\n".join([
            "Nome completo do aluno,CPF do aluno,Faixa,"
            "Nome completo do responsável legal,CPF do responsável legal",
            "Irmao Um,,Branca,Pai Teste,11122233344",
            "Irmao Dois,,Branca,Pai Teste,11122233344",
            "Irmao Tres,,Branca,Pai Teste,11122233344",
        ])
        monkeypatch.setattr(si, "_baixar_csv_robusto", lambda url: csv)
        resumo = si.importar_kids_de_url("x")
        assert resumo["importados"] == 3
        assert resumo["erros"] == []
