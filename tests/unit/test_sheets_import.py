"""Testes para importação via Google Sheets (funções puras + parsing)."""
import database.db as db
from utils import sheets_import as si


class TestNormalizacao:
    def test_norm_nome(self):
        assert si._norm_nome("  GLEIDISON   orique DO nascimento ") == "Gleidison Orique do Nascimento"
        assert si._norm_nome("maria da SILVA e souza") == "Maria da Silva e Souza"
        assert si._norm_nome("") == ""

    def test_norm_faixa(self):
        assert si._norm_faixa("marron") == "Marrom"
        assert si._norm_faixa("BRANCA") == "Branca"
        assert si._norm_faixa("roxa") == "Roxa"
        assert si._norm_faixa("0") == "Branca"
        assert si._norm_faixa("?") == "Branca"
        assert si._norm_faixa("") == "Branca"
        # valor desconhecido -> Branca
        assert si._norm_faixa("xpto") == "Branca"
        assert si._norm_faixa("Sem grau") == "Branca"

    def test_faixa_reconhecida(self):
        assert si._faixa_reconhecida("Azul") is True
        assert si._faixa_reconhecida("Amarela com branco") is True
        assert si._faixa_reconhecida("") is False
        assert si._faixa_reconhecida("xpto") is False
        assert si._faixa_reconhecida("1 dia") is False

    def test_norm_grau(self):
        assert si._norm_grau("1") == "1 Grau"
        assert si._norm_grau("2") == "2 Graus"
        assert si._norm_grau("4") == "4 Graus"
        assert si._norm_grau("Sem grau") == "Sem grau"
        assert si._norm_grau("") == "Sem grau"

    def test_conv_data(self):
        assert si._conv_data("04/06/1985") == "1985-06-04"
        assert si._conv_data("1985-06-04") == "1985-06-04"
        assert si._conv_data("") == ""


class TestCabecalhos:
    def _c(self, texto):
        return si._campo_do_cabecalho(si._normalizar(texto))

    def test_mapeamento_planilha_matricula(self):
        assert self._c("Nome completo") == "nome"
        assert self._c("CPF") == "cpf"
        assert self._c("Data de nascimento") == "data_nasc"
        assert self._c("Telefone (WhatsApp)") == "telefone"
        assert self._c("Faixa") == "faixa"
        assert self._c("E-mail") == "email"
        assert self._c("Endereço completo") == "endereco"
        assert self._c("Graus") == "grau"
        assert self._c("Tipo sanguíneo") == "tipo_sanguineo"
        assert self._c("Contato de emergência (nome e telefone)") == "contato_emergencia"
        assert self._c("Possui alguma alergia? Se sim, descreva") == "alergias"
        assert self._c("Quanto tempo de faixa?") == "tempo_faixa"

    def test_nao_mapeia_colunas_irrelevantes(self):
        # "Digite seu nome completo" não deve virar 'nome' (evita coluna errada)
        assert self._c("Digite seu nome completo") is None
        assert self._c("Carimbo de data/hora") is None


class TestExtrairUrl:
    def test_url_edicao(self):
        url = "https://docs.google.com/spreadsheets/d/ABC123_x-y/edit?gid=42#gid=42"
        assert si.extrair_csv_url(url) == (
            "https://docs.google.com/spreadsheets/d/ABC123_x-y/export?format=csv&gid=42"
        )

    def test_url_sem_gid(self):
        url = "https://docs.google.com/spreadsheets/d/ABC123/edit"
        assert si.extrair_csv_url(url).endswith("export?format=csv&gid=0")

    def test_url_invalida(self):
        import pytest
        with pytest.raises(ValueError):
            si.extrair_csv_url("http://exemplo.com/x")

    def test_candidatas_incluem_gviz(self):
        cands = si._urls_csv_candidatas("https://docs.google.com/spreadsheets/d/ID/edit?gid=7")
        assert any("export?format=csv" in c for c in cands)
        assert any("gviz/tq" in c for c in cands)


class TestImportacaoCompleta:
    def test_importa_e_normaliza(self, temp_db, monkeypatch):
        csv = "\n".join([
            "Nome completo,CPF,Data de nascimento,Telefone (WhatsApp),Faixa,"
            "E-mail,Endereço completo,Graus,Tipo sanguíneo,Quanto tempo de faixa?,"
            "Contato de emergência (nome e telefone)",
            "joão DA silva,111.222.333-96,04/06/1985,48 99999-9999,marron,"
            "a@a.com,Rua X 10,2,O+,2 anos,Maria 4899999",
        ])
        monkeypatch.setattr(si, "_baixar_csv_robusto", lambda url: csv)

        resumo = si.importar_alunos_de_url("qualquer", plano_padrao="Adulto - R$180")
        assert resumo["importados"] == 1
        assert resumo["erros"] == []

        conn = db.get_conn()
        cur = conn.cursor()
        cur.execute(
            "SELECT nome, faixa, grau, data_nascimento, telefone, plano, "
            "tipo_sanguineo, tempo_faixa, contato_emergencia FROM alunos"
        )
        row = cur.fetchone()
        conn.close()
        assert row[0] == "João da Silva"
        assert row[1] == "Marrom"
        assert row[2] == "2 Graus"
        assert row[3] == "1985-06-04"
        assert row[4] == "48999999999"  # só dígitos
        assert row[5] == "Adulto - R$180"
        assert row[6] == "O+"
        assert row[7] == "2 anos"
        assert "Maria" in (row[8] or "")

    def test_ignora_sem_nome_e_duplicado(self, temp_db, monkeypatch):
        csv = "\n".join([
            "Nome completo,CPF",
            ",12345678901",          # sem nome -> ignora
            "Fulano,12345678901",    # importa
            "Beltrano,12345678901",  # cpf duplicado -> ignora
        ])
        monkeypatch.setattr(si, "_baixar_csv_robusto", lambda url: csv)
        resumo = si.importar_alunos_de_url("x", plano_padrao="Adulto - R$180")
        assert resumo["importados"] == 1
        assert resumo["ignorados"] == 2

    def test_faixa_invalida_vira_branca_sem_grau(self, temp_db, monkeypatch):
        csv = "\n".join([
            "Nome completo,CPF,Faixa,Graus",
            "Sem Faixa,11111111111,,3",          # faixa vazia
            "Faixa Errada,22222222222,xpto,4",   # faixa invalida
            "Valida,33333333333,Azul,2",         # faixa valida
        ])
        monkeypatch.setattr(si, "_baixar_csv_robusto", lambda url: csv)
        si.importar_alunos_de_url("x", plano_padrao="Adulto - R$180")
        conn = db.get_conn()
        cur = conn.cursor()
        cur.execute("SELECT nome, faixa, grau FROM alunos ORDER BY nome")
        rows = {r[0]: (r[1], r[2]) for r in cur.fetchall()}
        conn.close()
        assert rows["Sem Faixa"] == ("Branca", "Sem grau")
        assert rows["Faixa Errada"] == ("Branca", "Sem grau")
        assert rows["Valida"] == ("Azul", "2 Graus")
