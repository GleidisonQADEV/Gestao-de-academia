from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit,
    QTableWidget, QTableWidgetItem, QMessageBox, QLabel
)
from database.db import connect
from ui.historico_dialog import HistoricoDialog


class AlunosTab(QWidget):
    def __init__(self, refresh_all):
        super().__init__()
        self.refresh_all = refresh_all
        self.build()
        self.load_alunos()

    # ---------------- UI ----------------

    def build(self):
        layout = QVBoxLayout(self)

        # ---------- BUSCA ----------
        busca_layout = QHBoxLayout()
        busca_layout.addWidget(QLabel("Buscar:"))

        self.busca = QLineEdit()
        self.busca.setPlaceholderText("Digite o nome do aluno...")
        self.busca.textChanged.connect(self.load_alunos)

        busca_layout.addWidget(self.busca)
        layout.addLayout(busca_layout)

        # ---------- FORM ----------
        form = QHBoxLayout()

        self.nome = QLineEdit()
        self.nome.setPlaceholderText("Nome")

        self.telefone = QLineEdit()
        self.telefone.setPlaceholderText("Telefone")

        self.mensal = QLineEdit()
        self.mensal.setPlaceholderText("Mensalidade")

        self.venc = QLineEdit()
        self.venc.setPlaceholderText("Dia vencimento")

        btn_add = QPushButton("Cadastrar")
        btn_add.clicked.connect(self.add_aluno)

        form.addWidget(self.nome)
        form.addWidget(self.telefone)
        form.addWidget(self.mensal)
        form.addWidget(self.venc)
        form.addWidget(btn_add)

        layout.addLayout(form)

        # ---------- TABELA ----------
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(6)
        self.tabela.setHorizontalHeaderLabels(
            ["ID", "Nome", "Telefone", "Mensal", "Venc", "Status"]
        )
        self.tabela.setSelectionBehavior(QTableWidget.SelectRows)

        # 👉 DUPLO CLIQUE = ABRIR HISTÓRICO
        self.tabela.cellDoubleClicked.connect(self.abrir_historico)

        layout.addWidget(self.tabela)

        # ---------- BOTÕES ----------
        btn_layout = QHBoxLayout()

        btn_inativar = QPushButton("Inativar / Reativar")
        btn_inativar.clicked.connect(self.toggle_status)

        btn_del = QPushButton("Excluir")
        btn_del.clicked.connect(self.del_aluno)

        btn_layout.addWidget(btn_inativar)
        btn_layout.addWidget(btn_del)

        layout.addLayout(btn_layout)

    # ---------------- DADOS ----------------

    def load_alunos(self):
        filtro = self.busca.text()

        conn = connect()
        cur = conn.cursor()

        if filtro:
            cur.execute("""
                SELECT * FROM alunos 
                WHERE nome LIKE ?
                ORDER BY nome
            """, (f"%{filtro}%",))
        else:
            cur.execute("SELECT * FROM alunos ORDER BY nome")

        rows = cur.fetchall()
        conn.close()

        self.tabela.setRowCount(0)

        for row in rows:
            r = self.tabela.rowCount()
            self.tabela.insertRow(r)
            for c, v in enumerate(row):
                self.tabela.setItem(r, c, QTableWidgetItem(str(v)))

    def add_aluno(self):
        try:
            if not self.nome.text():
                raise Exception("Informe o nome")

            conn = connect()
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO alunos (nome, telefone, valor_mensalidade, dia_vencimento, status)
                VALUES (?, ?, ?, ?, 'ATIVO')
            """, (
                self.nome.text(),
                self.telefone.text(),
                float(self.mensal.text()),
                int(self.venc.text())
            ))

            conn.commit()
            conn.close()

            self.nome.clear()
            self.telefone.clear()
            self.mensal.clear()
            self.venc.clear()

            self.load_alunos()
            self.refresh_all()

        except Exception as e:
            QMessageBox.warning(self, "Erro", str(e))

    def del_aluno(self):
        linha = self.tabela.currentRow()
        if linha < 0:
            return

        aluno_id = self.tabela.item(linha, 0).text()

        confirm = QMessageBox.question(
            self, "Excluir", "Deseja excluir este aluno?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.No:
            return

        conn = connect()
        cur = conn.cursor()
        cur.execute("DELETE FROM mensalidades WHERE aluno_id=?", (aluno_id,))
        cur.execute("DELETE FROM alunos WHERE id=?", (aluno_id,))
        conn.commit()
        conn.close()

        self.load_alunos()
        self.refresh_all()

    # ---------------- STATUS ----------------

    def toggle_status(self):
        linha = self.tabela.currentRow()
        if linha < 0:
            return

        aluno_id = self.tabela.item(linha, 0).text()
        status_atual = self.tabela.item(linha, 5).text()

        novo_status = "INATIVO" if status_atual == "ATIVO" else "ATIVO"

        conn = connect()
        cur = conn.cursor()
        cur.execute("UPDATE alunos SET status=? WHERE id=?", (novo_status, aluno_id))
        conn.commit()
        conn.close()

        self.load_alunos()
        self.refresh_all()

    # ---------------- HISTÓRICO ----------------

    def abrir_historico(self, row, col):
        aluno_id = self.tabela.item(row, 0).text()
        nome = self.tabela.item(row, 1).text()

        dlg = HistoricoDialog(aluno_id, nome)
        dlg.exec()
