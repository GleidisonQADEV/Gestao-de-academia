from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox
)

from database.db import connect


class AlunosTab(QWidget):
    def __init__(self, refresh_callbacks=None):
        super().__init__()
        self.refresh_callbacks = refresh_callbacks or []
        self.build()
        self.load_alunos()

    def build(self):
        layout = QVBoxLayout()
        form = QHBoxLayout()

        self.nome = QLineEdit()
        self.nome.setPlaceholderText("Nome")

        self.tel = QLineEdit()
        self.tel.setPlaceholderText("Telefone")

        self.valor = QLineEdit()
        self.valor.setPlaceholderText("Mensalidade")

        self.venc = QLineEdit()
        self.venc.setPlaceholderText("Dia vencimento")

        btn_add = QPushButton("Cadastrar")
        btn_add.clicked.connect(self.add_aluno)

        form.addWidget(self.nome)
        form.addWidget(self.tel)
        form.addWidget(self.valor)
        form.addWidget(self.venc)
        form.addWidget(btn_add)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(6)
        self.tabela.setHorizontalHeaderLabels(
            ["ID", "Nome", "Telefone", "Mensal", "Venc", "Status"]
        )

        btn_del = QPushButton("Excluir")
        btn_del.clicked.connect(self.del_aluno)

        layout.addLayout(form)
        layout.addWidget(self.tabela)
        layout.addWidget(btn_del)
        self.setLayout(layout)

    def add_aluno(self):
        try:
            nome = self.nome.text()
            tel = self.tel.text()
            valor = float(self.valor.text())
            venc = int(self.venc.text())

            if not nome:
                raise Exception("Nome obrigatório")

            conn = connect()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO alunos (nome, telefone, valor_mensalidade, dia_vencimento, status) "
                "VALUES (?, ?, ?, ?, 'ATIVO')",
                (nome, tel, valor, venc)
            )
            conn.commit()
            conn.close()

            self.nome.clear()
            self.tel.clear()
            self.valor.clear()
            self.venc.clear()

            self.load_alunos()
            self.refresh_all()

        except Exception as e:
            QMessageBox.warning(self, "Erro", str(e))

    def load_alunos(self):
        conn = connect()
        cur = conn.cursor()
        cur.execute("SELECT id, nome, telefone, valor_mensalidade, dia_vencimento, status FROM alunos")
        dados = cur.fetchall()
        conn.close()

        self.tabela.setRowCount(len(dados))
        for i, row in enumerate(dados):
            for j, val in enumerate(row):
                self.tabela.setItem(i, j, QTableWidgetItem(str(val)))

    def del_aluno(self):
        linha = self.tabela.currentRow()
        if linha < 0:
            return

        aluno_id = self.tabela.item(linha, 0).text()

        conn = connect()
        cur = conn.cursor()
        cur.execute("DELETE FROM mensalidades WHERE aluno_id=?", (aluno_id,))
        cur.execute("DELETE FROM alunos WHERE id=?", (aluno_id,))
        conn.commit()
        conn.close()

        self.load_alunos()
        self.refresh_all()

    def refresh_all(self):
        for cb in self.refresh_callbacks:
            cb()
