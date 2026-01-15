import os

from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QDateEdit, QComboBox, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QPixmap

from database.db import inserir_aluno


class CadastroAlunoTab(QWidget):
    def __init__(self, refresh_callback=None):
        super().__init__()
        self.refresh_callback = refresh_callback
        self.foto_path = None
        self.certificado_path = None
        self.build_ui()

    def build_ui(self):
        root = QVBoxLayout(self)
        root.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        root.setContentsMargins(0, 30, 0, 0)

        title = QLabel("Cadastro de Aluno")
        title.setStyleSheet("color: white; font-size: 26px; font-weight: bold;")
        root.addWidget(title, alignment=Qt.AlignCenter)

        form = QWidget()
        form_layout = QVBoxLayout(form)
        form_layout.setSpacing(14)

        LABEL_W = 140
        INPUT_W = 520
        SMALL_W = 240
        PREVIEW_W = 110
        BTN_W = 260

        def row(label_text, widget):
            h = QHBoxLayout()
            h.setAlignment(Qt.AlignLeft)
            label = QLabel(label_text)
            label.setFixedWidth(LABEL_W)
            label.setStyleSheet("color: white; font-size: 14px;")
            h.addWidget(label)
            h.addWidget(widget)
            return h

        input_style = """
            QLineEdit {
                background-color: #f2f2f2;
                padding: 12px;
                border-radius: 12px;
                border: 2px solid #ccc;
                font-size: 14px;
                color: #111;
            }
            QLineEdit:focus { border: 2px solid #e50914; }
        """

        combo_style = """
            QComboBox, QDateEdit {
                background-color: #f2f2f2;
                padding: 10px 38px 10px 12px;
                border-radius: 12px;
                border: 2px solid #ccc;
                font-size: 14px;
                color: #111;
            }
            QComboBox:focus, QDateEdit:focus { border: 2px solid #e50914; }

            QComboBox::drop-down, QDateEdit::drop-down {
                border: none;
                width: 34px;
                subcontrol-position: right center;
            }

            QComboBox::down-arrow, QDateEdit::down-arrow {
                image: none;
                width: 0; height: 0;
                border-left: 6px solid transparent;
                border-right: 6px solid transparent;
                border-top: 9px solid #e50914;
                margin-right: 12px;
            }
        """

        # ===== CAMPOS =====

        self.nome = QLineEdit()
        self.nome.setPlaceholderText("Nome completo")
        self.nome.setFixedWidth(INPUT_W)
        self.nome.setStyleSheet(input_style)
        form_layout.addLayout(row("Nome:", self.nome))

        self.cpf = QLineEdit()
        self.cpf.setInputMask("000.000.000-00")
        self.cpf.setFixedWidth(INPUT_W)
        self.cpf.setStyleSheet(input_style)
        form_layout.addLayout(row("CPF:", self.cpf))

        self.email = QLineEdit()
        self.email.setPlaceholderText("exemplo@email.com")
        self.email.setFixedWidth(INPUT_W)
        self.email.setStyleSheet(input_style)
        form_layout.addLayout(row("E-mail:", self.email))

        self.telefone = QLineEdit()
        self.telefone.setInputMask("(00) 00000-0000")
        self.telefone.setFixedWidth(INPUT_W)
        self.telefone.setStyleSheet(input_style)
        form_layout.addLayout(row("Telefone:", self.telefone))

        self.cep = QLineEdit()
        self.cep.setInputMask("00000-000")
        self.cep.setFixedWidth(SMALL_W)
        self.cep.setStyleSheet(input_style)

        cep_container = QWidget()
        cep_l = QHBoxLayout(cep_container)
        cep_l.setContentsMargins(0, 0, 0, 0)
        cep_l.addWidget(self.cep)
        cep_l.addStretch()
        cep_container.setFixedWidth(INPUT_W)
        form_layout.addLayout(row("CEP:", cep_container))

        self.endereco = QLineEdit()
        self.endereco.setPlaceholderText("Endereço completo")
        self.endereco.setFixedWidth(INPUT_W)
        self.endereco.setStyleSheet(input_style)
        form_layout.addLayout(row("Endereço:", self.endereco))

        # ===== NASCIMENTO =====
        self.data_input = QDateEdit()
        self.data_input.setCalendarPopup(True)
        self.data_input.setDate(QDate.currentDate())
        self.data_input.setFixedWidth(SMALL_W)
        self.data_input.setDisplayFormat("dd/MM/yyyy")
        self.data_input.setStyleSheet(combo_style)

        data_container = QWidget()
        data_l = QHBoxLayout(data_container)
        data_l.setContentsMargins(0, 0, 0, 0)
        data_l.addWidget(self.data_input)
        data_l.addStretch()
        data_container.setFixedWidth(INPUT_W)
        form_layout.addLayout(row("Nascimento:", data_container))

        # ===== FAIXA / GRAU =====
        faixa_grau_box = QHBoxLayout()
        faixa_grau_box.setSpacing(10)
        faixa_grau_box.setContentsMargins(0, 0, 0, 0)

        self.faixa = QComboBox()
        self.faixa.addItems(["Branca", "Azul", "Roxa", "Marrom", "Preta"])
        self.faixa.setFixedWidth(200)
        self.faixa.setStyleSheet(combo_style)

        self.grau = QComboBox()
        self.grau.addItems(["Sem grau", "1 Grau", "2 Graus", "3 Graus", "4 Graus"])
        self.grau.setFixedWidth(200)
        self.grau.setStyleSheet(combo_style)

        faixa_grau_box.addWidget(self.faixa)
        faixa_grau_box.addWidget(self.grau)
        faixa_grau_box.addStretch()

        faixa_container = QWidget()
        faixa_container.setLayout(faixa_grau_box)
        faixa_container.setFixedWidth(INPUT_W)
        form_layout.addLayout(row("Faixa / Grau:", faixa_container))

        # ===== FOTO (grade fixa) =====
        foto_grid = QHBoxLayout()
        foto_grid.setSpacing(12)
        foto_grid.setContentsMargins(0, 0, 0, 0)

        self.foto_label = QLabel("Sem foto")
        self.foto_label.setFixedSize(PREVIEW_W, 90)
        self.foto_label.setAlignment(Qt.AlignCenter)
        self.foto_label.setStyleSheet("background:#222;border-radius:10px;color:white;")

        btn_foto = QPushButton("Selecionar Foto")
        btn_foto.setFixedWidth(BTN_W)
        btn_foto.setStyleSheet(self.btn_style())
        btn_foto.clicked.connect(self.selecionar_foto)

        foto_grid.addWidget(self.foto_label)
        foto_grid.addWidget(btn_foto)
        foto_grid.addStretch()

        foto_container = QWidget()
        foto_container.setLayout(foto_grid)
        foto_container.setFixedWidth(INPUT_W)
        form_layout.addLayout(row("Foto:", foto_container))

        # ===== CERTIFICADO (mesma grade da foto) =====
        cert_grid = QHBoxLayout()
        cert_grid.setSpacing(12)
        cert_grid.setContentsMargins(0, 0, 0, 0)

        self.cert_label = QLabel()
        self.cert_label.setFixedWidth(PREVIEW_W)
        self.cert_label.setStyleSheet("color:white;")

        btn_cert = QPushButton("Anexar Certificado (PDF)")
        btn_cert.setFixedWidth(BTN_W)
        btn_cert.setStyleSheet(self.btn_style())
        btn_cert.clicked.connect(self.selecionar_certificado)

        cert_grid.addWidget(self.cert_label)
        cert_grid.addWidget(btn_cert)
        cert_grid.addStretch()

        cert_container = QWidget()
        cert_container.setLayout(cert_grid)
        cert_container.setFixedWidth(INPUT_W)
        form_layout.addLayout(row("Certificado:", cert_container))

        # ===== SALVAR =====
        btn = QPushButton("Salvar Aluno")
        btn.setFixedSize(240, 52)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #e50914;
                color: white;
                border-radius: 16px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #ff1a24; }
        """)
        btn.clicked.connect(self.salvar)

        form_layout.addSpacing(18)
        form_layout.addWidget(btn, alignment=Qt.AlignRight)
        root.addWidget(form)

    # -----------------------
    def btn_style(self):
        return """
            QPushButton {
                background-color: #e50914;
                color: white;
                border-radius: 10px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #ff1a24; }
        """

    def selecionar_foto(self):
        file, _ = QFileDialog.getOpenFileName(self, "Selecionar Foto", "", "Imagens (*.png *.jpg *.jpeg)")
        if file:
            self.foto_path = file
            pix = QPixmap(file).scaled(90, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.foto_label.setPixmap(pix)

    def selecionar_certificado(self):
        file, _ = QFileDialog.getOpenFileName(self, "Selecionar Certificado", "", "PDF (*.pdf)")
        if file:
            self.certificado_path = file
            self.cert_label.setText(os.path.basename(file))

    # -----------------------
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
            self.foto_path,
            self.certificado_path
        )

        QMessageBox.information(self, "Sucesso", "Aluno cadastrado com sucesso!")

        self.nome.clear()
        self.cpf.clear()
        self.email.clear()
        self.telefone.clear()
        self.cep.clear()
        self.endereco.clear()
        self.foto_label.setText("Sem foto")
        self.cert_label.setText("Nenhum PDF selecionado")
        self.foto_path = None
        self.certificado_path = None

        if self.refresh_callback:
            self.refresh_callback()
