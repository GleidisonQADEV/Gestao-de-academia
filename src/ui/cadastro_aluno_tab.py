import os

from PySide6.QtWidgets import (
    QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QDateEdit, QComboBox, QMessageBox, QFileDialog, QWidget
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QPixmap

from ui.base_tab import BaseTab
from database.db import inserir_aluno


class CadastroAlunoTab(BaseTab):
    def __init__(self, refresh_callback=None):
        super().__init__()
        self.refresh_callback = refresh_callback
        self.foto_path = None
        self.certificado_path = None
        self.build_ui()

    # -------------------------------------------------
    def build_ui(self):

        root = self.layout()

        container = QWidget()
        container.setMaximumWidth(760)

        form = QVBoxLayout(container)
        form.setSpacing(12)
        form.setAlignment(Qt.AlignTop)

        root.addWidget(container, alignment=Qt.AlignTop | Qt.AlignHCenter)

        # ---------------- CONFIGS ----------------
        LABEL_W = 130
        INPUT_W = 420
        SMALL_W = 190
        MINI_W = 200
        BTN_W = 150
        BTN_H = 36

        # ---------------- HELPERS ----------------
        def row(label_text, widget):
            h = QHBoxLayout()
            h.setSpacing(12)

            label = QLabel(label_text)
            label.setFixedWidth(LABEL_W)
            label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            label.setStyleSheet("color: white; font-size: 13px;")

            h.addWidget(label)
            h.addWidget(widget)
            h.addStretch()
            return h

        input_style = """
            QLineEdit, QDateEdit, QComboBox {
                background-color: rgba(255,255,255,0.95);
                padding: 7px 10px;
                border-radius: 10px;
                border: 1.5px solid #ccc;
                font-size: 13px;
                color: #111;
            }
            QLineEdit:focus, QDateEdit:focus, QComboBox:focus {
                border: 1.5px solid #e50914;
            }
            QComboBox::drop-down, QDateEdit::drop-down {
                border: none;
                width: 22px;
            }
            QComboBox::down-arrow, QDateEdit::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 8px solid #e50914;
                margin-right: 6px;
            }
        """

        def red_btn():
            return """
                QPushButton {
                    background-color: #e50914;
                    color: white;
                    border-radius: 9px;
                    padding: 6px 10px;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover { background-color: #ff1a24; }
            """

        # ---------------- TITLE ----------------
        title = QLabel("Cadastro de Aluno")
        title.setStyleSheet("color:white;font-size:22px;font-weight:bold;")
        form.addWidget(title, alignment=Qt.AlignLeft)
        form.addSpacing(6)

        # ---------------- CAMPOS ----------------
        self.nome = QLineEdit()
        self.nome.setPlaceholderText("Nome completo")
        self.nome.setFixedWidth(INPUT_W)
        self.nome.setStyleSheet(input_style)
        form.addLayout(row("Nome:", self.nome))

        self.cpf = QLineEdit()
        self.cpf.setInputMask("000.000.000-00")
        self.cpf.setFixedWidth(INPUT_W)
        self.cpf.setStyleSheet(input_style)
        form.addLayout(row("CPF:", self.cpf))

        self.email = QLineEdit()
        self.email.setPlaceholderText("exemplo@email.com")
        self.email.setFixedWidth(INPUT_W)
        self.email.setStyleSheet(input_style)
        form.addLayout(row("E-mail:", self.email))

        self.telefone = QLineEdit()
        self.telefone.setInputMask("(00) 00000-0000")
        self.telefone.setFixedWidth(INPUT_W)
        self.telefone.setStyleSheet(input_style)
        form.addLayout(row("Telefone:", self.telefone))

        self.cep = QLineEdit()
        self.cep.setInputMask("00000-000")
        self.cep.setFixedWidth(SMALL_W)
        self.cep.setStyleSheet(input_style)
        form.addLayout(row("CEP:", self.cep))

        self.endereco = QLineEdit()
        self.endereco.setPlaceholderText("Endereço completo")
        self.endereco.setFixedWidth(INPUT_W)
        self.endereco.setStyleSheet(input_style)
        form.addLayout(row("Endereço:", self.endereco))

        self.data_input = QDateEdit()
        self.data_input.setCalendarPopup(True)
        self.data_input.setDate(QDate.currentDate())
        self.data_input.setDisplayFormat("dd/MM/yyyy")
        self.data_input.setFixedWidth(SMALL_W)
        self.data_input.setStyleSheet(input_style)
        form.addLayout(row("Nascimento:", self.data_input))

        # -------- FAIXA / GRAU (alinhado exato) --------
        faixa_wrap = QWidget()
        faixa_row = QHBoxLayout(faixa_wrap)
        faixa_row.setSpacing(10)
        faixa_row.setContentsMargins(0, 0, 0, 0)

        self.faixa = QComboBox()
        self.faixa.addItems(["Branca", "Azul", "Roxa", "Marrom", "Preta"])
        self.faixa.setFixedWidth(MINI_W)
        self.faixa.setStyleSheet(input_style)

        self.grau = QComboBox()
        self.grau.addItems(["Sem grau", "1 Grau", "2 Graus", "3 Graus", "4 Graus"])
        self.grau.setFixedWidth(MINI_W)
        self.grau.setStyleSheet(input_style)

        faixa_row.addWidget(self.faixa)
        faixa_row.addWidget(self.grau)
        faixa_row.addStretch()

        form.addLayout(row("Faixa / Grau:", faixa_wrap))

        # -------- PESO / ALTURA (alinhado exato) --------
        pa_wrap = QWidget()
        pa_row = QHBoxLayout(pa_wrap)
        pa_row.setSpacing(10)
        pa_row.setContentsMargins(0, 0, 0, 0)

        self.peso = QLineEdit()
        self.peso.setPlaceholderText("kg")
        self.peso.setFixedWidth(120)
        self.peso.setStyleSheet(input_style)

        self.altura = QLineEdit()
        self.altura.setPlaceholderText("cm")
        self.altura.setFixedWidth(120)
        self.altura.setStyleSheet(input_style)

        pa_row.addWidget(self.peso)
        pa_row.addWidget(self.altura)
        pa_row.addStretch()

        form.addLayout(row("Peso / Altura:", pa_wrap))

        # -------- PLANO --------
        self.plano = QComboBox()
        self.plano.addItems([
            "Adulto - R$180",
            "Kids (5–13) - R$150",
            "Família: 2 adultos - R$320",
            "Família: 1 adulto + 1 kids - R$300",
            "Família: 2 adultos + 1 kids - R$450",
            "Família: 1 adulto + 2 kids - R$430",
            "Família: 1 adulto + 3 kids - R$500"
        ])
        self.plano.setFixedWidth(INPUT_W)
        self.plano.setStyleSheet(input_style)
        form.addLayout(row("Plano:", self.plano))

        # -------- FOTO / CERT (botões menores) --------
        files_wrap = QWidget()
        files_row = QHBoxLayout(files_wrap)
        files_row.setSpacing(10)
        files_row.setContentsMargins(0, 0, 0, 0)

        self.foto_label = QLabel()
        self.foto_label.setFixedSize(70, 70)
        self.foto_label.setStyleSheet("background:#222;border-radius:8px;")

        btn_foto = QPushButton("Selecionar Foto")
        btn_foto.setFixedSize(BTN_W, BTN_H)
        btn_foto.setStyleSheet(red_btn())
        btn_foto.clicked.connect(self.selecionar_foto)

        btn_cert = QPushButton("Anexar Certificado")
        btn_cert.setFixedSize(BTN_W, BTN_H)
        btn_cert.setStyleSheet(red_btn())
        btn_cert.clicked.connect(self.selecionar_certificado)

        files_row.addWidget(self.foto_label)
        files_row.addWidget(btn_foto)
        files_row.addWidget(btn_cert)
        files_row.addStretch()

        form.addLayout(row("Arquivos:", files_wrap))

        # -------- BOTÃO SALVAR (CANTO DIREITO) --------
        btn = QPushButton("Salvar Aluno")
        btn.setFixedSize(200, 44)
        btn.setStyleSheet(red_btn())
        btn.clicked.connect(self.salvar)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(btn)

        form.addSpacing(8)
        form.addLayout(btn_row)

    # -------------------------------------------------
    def selecionar_foto(self):
        file, _ = QFileDialog.getOpenFileName(self, "Selecionar Foto", "", "Imagens (*.png *.jpg *.jpeg)")
        if file:
            self.foto_path = file
            pix = QPixmap(file).scaled(70, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.foto_label.setPixmap(pix)

    def selecionar_certificado(self):
        file, _ = QFileDialog.getOpenFileName(self, "Selecionar Certificado", "", "PDF (*.pdf)")
        if file:
            self.certificado_path = file

    # -------------------------------------------------
    def salvar(self):
        inserir_aluno(
            self.nome.text(),
            self.cpf.text(),
            self.email.text(),
            self.telefone.text(),
            self.cep.text(),
            self.endereco.text(),
            self.data_input.date().toString("yyyy-MM-dd"),
            self.faixa.currentText(),
            self.grau.currentText(),
            self.peso.text(),
            self.altura.text(),
            self.plano.currentText(),
            self.foto_path,
            self.certificado_path
        )

        QMessageBox.information(self, "Sucesso", "Aluno cadastrado com sucesso!")

        if self.refresh_callback:
            self.refresh_callback()
