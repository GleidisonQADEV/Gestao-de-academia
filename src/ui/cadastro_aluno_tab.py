import os

from PySide6.QtWidgets import (
    QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QDateEdit, QComboBox, QFileDialog, QWidget, QCheckBox
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QPixmap

from ui.base_tab import BaseTab
from ui.app_dialog import AppDialog
from database.db import inserir_aluno, cpf_existe, email_existe
from database.kids_db import inserir_kid, cpf_kid_existe


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

        # -------- TAMANHOS --------
        LABEL_W = 130
        INPUT_W = 420
        SMALL_W = 190
        MINI_W = 200
        CPF_W = 260
        BTN_W = 150
        BTN_H = 36

        # -------- HELPERS --------
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

        # -------- TITLE --------
        title = QLabel("Cadastro de Aluno")
        title.setStyleSheet("color:white;font-size:22px;font-weight:bold;")
        form.addWidget(title, alignment=Qt.AlignLeft)

        # -------- LEGENDA CAMPOS OBRIGATÓRIOS --------
        legenda = QLabel("* Campos obrigatórios")
        legenda.setStyleSheet("color:#ff6666;font-size:11px;font-style:italic;margin-bottom:10px;")
        form.addWidget(legenda, alignment=Qt.AlignLeft)

        # -------- KIDS CHECK --------
        self.chk_kids = QCheckBox("Aluno Kids (menor de 16)")
        self.chk_kids.setStyleSheet("color:white;font-weight:bold;")
        self.chk_kids.stateChanged.connect(self.toggle_responsavel)
        form.addWidget(self.chk_kids)

        # -------- NOME --------
        self.nome = QLineEdit()
        self.nome.setPlaceholderText("Digite o nome completo *")
        self.nome.setFixedWidth(INPUT_W)
        self.nome.setStyleSheet(input_style)
        form.addLayout(row("Nome:", self.nome))

        # -------- CPF (OPCIONAL PARA KIDS) --------
        self.cpf = QLineEdit()
        self.cpf.setInputMask("000.000.000-00")
        self.cpf.setPlaceholderText("Opcional para Kids - será gerado automaticamente se vazio")
        self.cpf.setFixedWidth(CPF_W)
        self.cpf.setStyleSheet(input_style)
        form.addLayout(row("CPF:", self.cpf))

        # -------- RESPONSÁVEL (KIDS) --------
        self.resp_wrap = QWidget()
        resp_layout = QVBoxLayout(self.resp_wrap)
        resp_layout.setContentsMargins(0, 0, 0, 0)
        resp_layout.setSpacing(12)

        self.resp_nome = QLineEdit()
        self.resp_nome.setPlaceholderText("Nome do responsável *")
        self.resp_nome.setFixedWidth(INPUT_W)
        self.resp_nome.setStyleSheet(input_style)
        resp_layout.addLayout(row("Resp. Nome:", self.resp_nome))

        self.resp_cpf = QLineEdit()
        self.resp_cpf.setInputMask("000.000.000-00")
        self.resp_cpf.setPlaceholderText("CPF do responsável *")
        self.resp_cpf.setFixedWidth(CPF_W)
        self.resp_cpf.setStyleSheet(input_style)
        resp_layout.addLayout(row("Resp. CPF:", self.resp_cpf))

        self.resp_wrap.setVisible(False)
        form.addWidget(self.resp_wrap)

        # -------- EMAIL --------
        self.email = QLineEdit()
        self.email.setPlaceholderText("exemplo@email.com (opcional)")
        self.email.setFixedWidth(INPUT_W)
        self.email.setStyleSheet(input_style)
        form.addLayout(row("E-mail:", self.email))

        # -------- TELEFONE --------
        self.telefone = QLineEdit()
        self.telefone.setInputMask("(00) 00000-0000")
        self.telefone.setPlaceholderText("(00) 00000-0000 *")
        self.telefone.setFixedWidth(MINI_W)
        self.telefone.setStyleSheet(input_style)
        form.addLayout(row("Telefone:", self.telefone))

        # -------- CEP --------
        self.cep = QLineEdit()
        self.cep.setInputMask("00000-000")
        self.cep.setPlaceholderText("00000-000 *")
        self.cep.setFixedWidth(SMALL_W)
        self.cep.setStyleSheet(input_style)
        form.addLayout(row("CEP:", self.cep))

        # -------- ENDEREÇO --------
        self.endereco = QLineEdit()
        self.endereco.setPlaceholderText("Rua, número, bairro *")
        self.endereco.setFixedWidth(INPUT_W)
        self.endereco.setStyleSheet(input_style)
        form.addLayout(row("Endereço:", self.endereco))

        # -------- NASCIMENTO --------
        self.data_input = QDateEdit()
        self.data_input.setCalendarPopup(True)
        self.data_input.setDate(QDate.currentDate())
        self.data_input.setDisplayFormat("dd/MM/yyyy")
        self.data_input.setFixedWidth(SMALL_W)
        self.data_input.setStyleSheet(input_style)
        form.addLayout(row("Nascimento:", self.data_input))

        # -------- FAIXA / GRAU --------
        self.faixa = QComboBox()
        self.faixa.addItems(["Branca", "Azul", "Roxa", "Marrom", "Preta"])
        self.faixa.setFixedWidth(MINI_W)
        self.faixa.setStyleSheet(input_style)

        self.grau = QComboBox()
        self.grau.addItems(["Sem grau", "1 Grau", "2 Graus", "3 Graus", "4 Graus"])
        self.grau.setFixedWidth(MINI_W)
        self.grau.setStyleSheet(input_style)

        fw = QWidget()
        fw.setFixedWidth(INPUT_W)
        fl = QHBoxLayout(fw)
        fl.setContentsMargins(0, 0, 0, 0)
        fl.setSpacing(12)
        fl.addWidget(self.faixa)
        fl.addWidget(self.grau)
        form.addLayout(row("Faixa / Grau:", fw))

        # -------- PESO / ALTURA --------
        self.peso = QLineEdit()
        self.peso.setPlaceholderText("Peso (kg)")
        self.peso.setFixedWidth(MINI_W)
        self.peso.setStyleSheet(input_style)

        self.altura = QLineEdit()
        self.altura.setPlaceholderText("Altura (cm)")
        self.altura.setFixedWidth(MINI_W)
        self.altura.setStyleSheet(input_style)

        pw = QWidget()
        pw.setFixedWidth(INPUT_W)
        pl = QHBoxLayout(pw)
        pl.setContentsMargins(0, 0, 0, 0)
        pl.setSpacing(12)
        pl.addWidget(self.peso)
        pl.addWidget(self.altura)
        form.addLayout(row("Peso / Altura:", pw))

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

        # -------- ARQUIVOS --------
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

        aw = QWidget()
        al = QHBoxLayout(aw)
        al.setContentsMargins(0, 0, 0, 0)
        al.setSpacing(10)
        al.addWidget(self.foto_label)
        al.addWidget(btn_foto)
        al.addWidget(btn_cert)
        al.addStretch()
        form.addLayout(row("Arquivos:", aw))

        # -------- BOTÃO --------
        btn = QPushButton("Salvar Aluno")
        btn.setFixedSize(200, 44)
        btn.setStyleSheet(red_btn())
        btn.clicked.connect(self.salvar)

        br = QHBoxLayout()
        br.addStretch()
        br.addWidget(btn)
        form.addLayout(br)

    # -------------------------------------------------

    def limpar_formulario(self):
        """Limpa todos os campos do formulário após salvar"""
        # Campos principais
        self.nome.clear()
        self.cpf.clear()
        self.email.clear()
        self.telefone.clear()
        self.cep.clear()
        self.endereco.clear()
        self.peso.clear()
        self.altura.clear()
        
        # Campos do responsável
        self.resp_nome.clear()
        self.resp_cpf.clear()
        
        # Resetar comboboxes para primeira opção
        self.faixa.setCurrentIndex(0)
        self.grau.setCurrentIndex(0)
        self.plano.setCurrentIndex(0)
        
        # Resetar data para hoje
        self.data_input.setDate(QDate.currentDate())
        
        # Resetar checkbox kids
        self.chk_kids.setChecked(False)
        
        # Limpar foto e certificado
        self.foto_path = None
        self.certificado_path = None
        self.foto_label.clear()
        self.foto_label.setStyleSheet("background:#222;border-radius:8px;")
        
        # Esconder seção do responsável
        self.resp_wrap.setVisible(False)

    def toggle_responsavel(self):
        self.resp_wrap.setVisible(self.chk_kids.isChecked())

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

        nome = self.nome.text().strip()
        cpf_raw = "".join(filter(str.isdigit, self.cpf.text()))
        cpf = cpf_raw if cpf_raw else None

        telefone = "".join(filter(str.isdigit, self.telefone.text()))
        cep = "".join(filter(str.isdigit, self.cep.text()))
        endereco = self.endereco.text().strip()
        email = self.email.text().strip()
        peso = self.peso.text().strip()
        altura = self.altura.text().strip()
        faixa = self.faixa.currentText()
        grau = self.grau.currentText()
        plano = self.plano.currentText()
        data_nasc = self.data_input.date().toString("yyyy-MM-dd")

        is_kid = self.chk_kids.isChecked()

        if not nome:
            AppDialog("Atenção", "Nome obrigatório.", ("OK",), self).exec()
            return

        # Validar telefone obrigatório
        if len(telefone) < 10:
            AppDialog("Atenção", "Telefone obrigatório (mínimo 10 dígitos).", ("OK",), self).exec()
            return

        # Validar CEP obrigatório
        if len(cep) != 8:
            AppDialog("Atenção", "CEP obrigatório (8 dígitos).", ("OK",), self).exec()
            return

        # Validar endereço obrigatório
        if not endereco:
            AppDialog("Atenção", "Endereço obrigatório.", ("OK",), self).exec()
            return

        # Validar data de nascimento (não pode ser futura)
        data_atual = QDate.currentDate()
        if self.data_input.date() > data_atual:
            AppDialog("Atenção", "Data de nascimento não pode ser futura.", ("OK",), self).exec()
            return

        # Validar se não é muito antiga (mais de 100 anos)
        if self.data_input.date().addYears(100) < data_atual:
            AppDialog("Atenção", "Data de nascimento inválida (mais de 100 anos).", ("OK",), self).exec()
            return

        # Validar faixa e plano (não devem estar vazios)
        if not faixa or faixa == "":
            AppDialog("Atenção", "Faixa obrigatória.", ("OK",), self).exec()
            return

        if not plano or plano == "":
            AppDialog("Atenção", "Plano obrigatório.", ("OK",), self).exec()
            return

        # ===== ADULTO =====
        if not is_kid:
            # Validar idade para adultos (mínimo 16 anos)
            data_nasc_date = self.data_input.date()
            idade = data_atual.year() - data_nasc_date.year()
            if data_atual < data_nasc_date.addYears(idade):
                idade -= 1
            
            if idade < 16:
                AppDialog("Atenção", "Alunos adultos devem ter pelo menos 16 anos.", ("OK",), self).exec()
                return
                
            if not cpf or len(cpf) != 11:
                AppDialog("Atenção", "CPF inválido.", ("OK",), self).exec()
                return

        # ===== KIDS =====
        if is_kid:
            # Validar idade para Kids (5-16 anos)
            data_nasc_date = self.data_input.date()
            idade = data_atual.year() - data_nasc_date.year()
            if data_atual < data_nasc_date.addYears(idade):
                idade -= 1
            
            if idade < 5 or idade > 16:
                AppDialog("Atenção", "Alunos Kids devem ter entre 5 e 16 anos.", ("OK",), self).exec()
                return
            
            resp_nome = self.resp_nome.text().strip()
            resp_cpf = "".join(filter(str.isdigit, self.resp_cpf.text()))

            if not resp_nome or len(resp_cpf) != 11:
                AppDialog("Atenção", "Dados do responsável obrigatórios.", ("OK",), self).exec()
                return

            if cpf and cpf_kid_existe(cpf):
                AppDialog("Erro", "CPF do aluno já cadastrado (Kids).", ("OK",), self).exec()
                return

            try:
                inserir_kid(
                    nome, cpf, resp_nome, resp_cpf, email,
                    telefone, cep, endereco,
                    data_nasc, faixa, grau, peso, altura,
                    plano, self.foto_path, self.certificado_path
                )
            except Exception as e:
                AppDialog("Erro", f"Erro ao cadastrar aluno: {str(e)}", ("OK",), self).exec()
                return

        # ===== ADULTO =====
        else:
            if cpf_existe(cpf):
                AppDialog("Erro", "CPF já cadastrado.", ("OK",), self).exec()
                return

            if email and email_existe(email):
                AppDialog("Erro", "E-mail já cadastrado.", ("OK",), self).exec()
                return

            try:
                inserir_aluno(
                    nome, cpf, email, telefone, cep,
                    endereco, data_nasc, faixa, grau, peso, altura,
                    plano, self.foto_path, self.certificado_path
                )
            except Exception as e:
                AppDialog("Erro", f"Erro ao cadastrar aluno: {str(e)}", ("OK",), self).exec()
                return

        AppDialog("Sucesso", "Cadastro realizado com sucesso!", ("OK",), self).exec()

        # Limpar formulário após salvar
        self.limpar_formulario()

        if self.refresh_callback:
            self.refresh_callback()
