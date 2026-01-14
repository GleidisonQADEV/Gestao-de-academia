from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QLabel, QComboBox
)
from PySide6.QtGui import QColor
from database.db import connect
from ui.aluno_profile import AlunoProfile


FAIXAS = ["Branca", "Azul", "Roxa", "Marrom", "Preta"]

FAIXA_CORES = {
    "Branca": "#f9fafb",
    "Azul": "#2563eb",
    "Roxa": "#7c3aed",
    "Marrom": "#92400e",
    "Preta": "#111827"
}


class AlunosTab(QWidget):
    def __init__(self, refresh_all):
        super().__init__()
        self.refresh_all = refresh_all
        self.build()
        self.load()

    # ---------------- UI ----------------

    def build(self):
        layout = QVBoxLayout(self)

        # ---------- FORM 1 ----------
        form1 = QHBoxLayout()
        self.nome = QLineEdit(); self.nome.setPlaceholderText("Nome completo")
        self.cpf = QLineEdit(); self.cpf.setPlaceholderText("CPF")
        self.nasc = QLineEdit(); self.nasc.setPlaceholderText("Nascimento (DD/MM/AAAA)")
        self.tel = QLineEdit(); self.tel.setPlaceholderText("Telefone")

        form1.addWidget(self.nome)
        form1.addWidget(self.cpf)
        form1.addWidget(self.nasc)
        form1.addWidget(self.tel)

        # ---------- FORM 2 ----------
        form2 = QHBoxLayout()

        self.faixa = QComboBox()
        self.faixa.addItems(FAIXAS)
        self.faixa.setMinimumWidth(140)
        self.faixa.view().setMinimumWidth(160)
        self.faixa.setSizeAdjustPolicy(QComboBox.AdjustToContents)

        self.email = QLineEdit(); self.email.setPlaceholderText("E-mail")
        self.endereco = QLineEdit(); self.endereco.setPlaceholderText("Endereço")

        form2.addWidget(QLabel("Faixa:"))
        form2.addWidget(self.faixa)
        form2.addWidget(self.email)
        form2.addWidget(self.endereco)

        # ---------- FORM 3 ----------
        form3 = QHBoxLayout()

        self.valor = QLineEdit(); self.valor.setPlaceholderText("Mensalidade (R$)")
        self.venc = QLineEdit(); self.venc.setPlaceholderText("Dia vencimento")

        btn_add = QPushButton("Cadastrar Aluno")
        btn_add.clicked.connect(self.add_aluno)

        btn_inativar = QPushButton("Inativar / Ativar")
        btn_inativar.setObjectName("secondary")
        btn_inativar.clicked.connect(self.toggle_status)

        form3.addWidget(self.valor)
        form3.addWidget(self.venc)
        form3.addWidget(btn_add)
        form3.addWidget(btn_inativar)

        # ---------- TABELA ----------
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(7)
        self.tabela.setHorizontalHeaderLabels([
            "ID", "Nome", "CPF", "Telefone", "Faixa", "Mensalidade", "Status"
        ])
        self.tabela.setColumnHidden(0, True)
        self.tabela.cellDoubleClicked.connect(self.open_profile)

        layout.addLayout(form1)
        layout.addLayout(form2)
        layout.addLayout(form3)
        layout.addWidget(self.tabela)

    # ---------------- AÇÕES ----------------

    def add_aluno(self):
        try:
            conn = connect()
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO alunos
                (nome, cpf, data_nascimento, telefone, faixa, email, endereco,
                 valor_mensalidade, dia_vencimento, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'ATIVO')
            """, (
                self.nome.text(),
                self.cpf.text(),
                self.nasc.text(),
                self.tel.text(),
                self.faixa.currentText(),
                self.email.text(),
                self.endereco.text(),
                float(self.valor.text()),
                int(self.venc.text())
            ))

            conn.commit()
            conn.close()

            self.clear_form()
            self.load()
            self.refresh_all()

        except Exception as e:
            QMessageBox.warning(self, "Erro", str(e))

    def load(self):
        conn = connect()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, nome, cpf, telefone, faixa, valor_mensalidade, status
            FROM alunos
            ORDER BY nome
        """)
        rows = cur.fetchall()
        conn.close()

        self.tabela.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                item = QTableWidgetItem(str(val))

                # --- Estiliza faixa ---
                if j == 4:  # coluna Faixa
                    faixa = str(val)
                    item.setText(f"🥋 {faixa}")
                    cor = FAIXA_CORES.get(faixa, "#111827")
                    item.setForeground(QColor(cor))

                self.tabela.setItem(i, j, item)

    def toggle_status(self):
        row = self.tabela.currentRow()
        if row < 0:
            return

        aluno_id = self.tabela.item(row, 0).text()
        status = self.tabela.item(row, 6).text()

        novo = "INATIVO" if status == "ATIVO" else "ATIVO"

        conn = connect()
        cur = conn.cursor()
        cur.execute("UPDATE alunos SET status=? WHERE id=?", (novo, aluno_id))
        conn.commit()
        conn.close()

        self.load()
        self.refresh_all()

    def open_profile(self, row, col):
        aluno_id = self.tabela.item(row, 0).text()
        self.profile = AlunoProfile(aluno_id)
        self.profile.setWindowTitle("Perfil do Aluno")
        self.profile.resize(720, 480)
        self.profile.show()

    def clear_form(self):
        for f in [
            self.nome, self.cpf, self.nasc, self.tel,
            self.email, self.endereco, self.valor, self.venc
        ]:
            f.clear()
