import os

from PySide6.QtWidgets import (
    QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QDateEdit, QComboBox, QFileDialog, QWidget, QCheckBox
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QPixmap

from ui.base_tab import BaseTab
from ui.app_dialog import AppDialog, show_info, show_question
from database.db import inserir_aluno, cpf_existe, email_existe, get_planos_formatados
from database.kids_db import inserir_kid, cpf_kid_existe


class CadastroAlunoTab(BaseTab):
    def __init__(self, refresh_callback=None):
        super().__init__()
        self.refresh_callback = refresh_callback
        self.foto_path = None
        self.certificado_path = None

        # listas de faixas
        self.faixas_adulto = ["Branca", "Azul", "Roxa", "Marrom", "Preta"]
        self.faixas_kids = [
            "Branca",
            "Cinza c/b", "Cinza", "Cinza c/p",
            "Amarela c/b", "Amarela", "Amarela c/p",
            "Laranja c/b", "Laranja", "Laranja c/p",
            "Verde c/b", "Verde", "Verde c/p"
        ]

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

        legenda = QLabel("* Campos obrigatórios")
        legenda.setStyleSheet("color:#ff6666;font-size:11px;font-style:italic;margin-bottom:10px;")
        form.addWidget(legenda, alignment=Qt.AlignLeft)

        # -------- KIDS CHECK --------
        self.chk_kids = QCheckBox("Aluno Kids (menor de 16)")
        self.chk_kids.setStyleSheet("color:white;font-weight:bold;")
        self.chk_kids.stateChanged.connect(self.toggle_responsavel)
        self.chk_kids.stateChanged.connect(self.atualizar_faixas)
        form.addWidget(self.chk_kids)

        # -------- NOME --------
        self.nome = QLineEdit()
        self.nome.setPlaceholderText("Digite o nome completo *")
        self.nome.setFixedWidth(INPUT_W)
        self.nome.setStyleSheet(input_style)
        form.addLayout(row("Nome:", self.nome))

        # -------- CPF --------
        self.cpf = QLineEdit()
        self.cpf.setInputMask("000.000.000-00")
        self.cpf.setPlaceholderText("Opcional para Kids - será gerado automaticamente se vazio")
        self.cpf.setFixedWidth(CPF_W)
        self.cpf.setStyleSheet(input_style)
        form.addLayout(row("CPF:", self.cpf))

        # -------- RESPONSÁVEL --------
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
        self.faixa.addItems(self.faixas_adulto)
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
        self.carregar_planos()
        self.plano.setFixedWidth(INPUT_W)
        self.plano.setStyleSheet(input_style)
        self.plano.currentTextChanged.connect(self.toggle_plano_personalizado)
        form.addLayout(row("Plano:", self.plano))

        # campo valor personalizado
        self.valor_personalizado = QLineEdit()
        self.valor_personalizado.setPlaceholderText("Digite o valor (ex: 99.90)")
        self.valor_personalizado.setFixedWidth(MINI_W)
        self.valor_personalizado.setStyleSheet(input_style)

        self.valor_plano_wrap = QWidget()
        vpl = QHBoxLayout(self.valor_plano_wrap)
        vpl.setContentsMargins(0, 0, 0, 0)
        vpl.addLayout(row("Valor do Plano:", self.valor_personalizado))

        form.addWidget(self.valor_plano_wrap)
        self.valor_plano_wrap.setVisible(False)

        # -------- AVISO FINANCEIRO --------
        aviso_financeiro = QLabel("A data de pgto deve ser ajustada em \"editar\" na aba financeiro")
        aviso_financeiro.setStyleSheet("color:#ff6666;font-size:11px;font-style:italic;margin:5px 0px;")
        aviso_financeiro.setWordWrap(True)
        
        # Criar layout para centralizar o aviso
        aviso_layout = QHBoxLayout()
        aviso_layout.addStretch()
        aviso_layout.addWidget(aviso_financeiro)
        aviso_layout.addStretch()
        form.addLayout(aviso_layout)

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
        
        btn_biometria = QPushButton("🔍 Cadastrar Biometria")
        btn_biometria.setFixedSize(BTN_W + 20, BTN_H)
        btn_biometria.setStyleSheet(red_btn())
        btn_biometria.clicked.connect(self.cadastrar_biometria)

        aw = QWidget()
        al = QHBoxLayout(aw)
        al.setContentsMargins(0, 0, 0, 0)
        al.setSpacing(10)
        al.addWidget(self.foto_label)
        al.addWidget(btn_foto)
        al.addWidget(btn_cert)
        al.addWidget(btn_biometria)
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

    def atualizar_faixas(self):
        self.faixa.clear()
        if self.chk_kids.isChecked():
            self.faixa.addItems(self.faixas_kids)
        else:
            self.faixa.addItems(self.faixas_adulto)

    def toggle_plano_personalizado(self):
        texto = self.plano.currentText()
        mostrar = texto == "Plano Personalizado"
        self.valor_plano_wrap.setVisible(mostrar)

    def carregar_planos(self):
        """Carrega planos do banco de dados"""
        try:
            self.plano.clear()
            planos = get_planos_formatados()
            self.plano.addItems(planos)
        except Exception as e:
            # Fallback para planos padrão em caso de erro
            self.plano.addItems([
                "Adulto - R$180",
                "Kids (5–13) - R$150",
                "Plano Personalizado"
            ])

    def limpar_formulario(self):
        self.nome.clear()
        self.cpf.clear()
        self.email.clear()
        self.telefone.clear()
        self.cep.clear()
        self.endereco.clear()
        self.peso.clear()
        self.altura.clear()
        self.resp_nome.clear()
        self.resp_cpf.clear()
        self.faixa.setCurrentIndex(0)
        self.grau.setCurrentIndex(0)
        self.carregar_planos()  # Recarregar planos atualizados
        self.plano.setCurrentIndex(0)
        self.valor_personalizado.clear()
        self.data_input.setDate(QDate.currentDate())
        self.chk_kids.setChecked(False)
        self.foto_path = None
        self.certificado_path = None
        self.biometria_data = None
        self.foto_label.clear()
        self.foto_label.setStyleSheet("background:#222;border-radius:8px;")
        self.foto_label.clear()
        self.foto_label.setStyleSheet("background:#222;border-radius:8px;")
        self.resp_wrap.setVisible(False)

    def toggle_responsavel(self):
        is_kid = self.chk_kids.isChecked()
        self.resp_wrap.setVisible(is_kid)

        self.plano.blockSignals(True)
        self.plano.clear()

        if is_kid:
            self.plano.addItems([
                "Kids (5–13) - R$150",
                "Plano Personalizado",
                "Plano Bolsista (Patrocinado)"
            ])
        else:
            self.plano.addItems([
                "Adulto - R$180",
                "Kids (5–13) - R$150",
                "Família: 2 adultos - R$320",
                "Família: 1 adulto + 1 kids - R$300",
                "Família: 2 adultos + 1 kids - R$450",
                "Família: 1 adulto + 2 kids - R$430",
                "Família: 1 adulto + 3 kids - R$500",
                "Plano Personalizado",
                "Plano Bolsista (Patrocinado)"
            ])

        self.plano.setCurrentIndex(0)
        self.plano.blockSignals(False)

        self.toggle_plano_personalizado()


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
            
    def cadastrar_biometria(self):
        """Simula cadastro de biometria"""
        resultado = show_question(
            self,
            "Cadastrar Biometria",
            "📱 Conecte o leitor biométrico e posicione o dedo.\n\nSimular cadastro de biometria?",
            "Sim", "Cancelar"
        )
        
        if resultado:
            import random
            self.biometria_data = {
                "template": f"BIO_{random.randint(1000,9999)}",
                "quality": random.randint(85, 98)
            }
            
            show_info(self, "Sucesso", f"🎉 Biometria cadastrada!\n\nQualidade: {self.biometria_data['quality']:.0f}%")
            
    def confirmar_salvamento(self):
        dlg = AppDialog(
            "Confirmar Cadastro",
            "Confira se todos os dados estão corretos.\n\nDeseja salvar o cadastro?",
            ("Cancelar", "Confirmar"),
            self
        )
        dlg.exec()
        return dlg.clicked



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

        plano_texto = self.plano.currentText()
        if plano_texto == "Plano Personalizado":
            valor = self.valor_personalizado.text().strip()
            if not valor:
                AppDialog("Atenção", "Informe o valor do plano personalizado.", ("OK",), self).exec()
                return
            plano = f"Personalizado - R${valor}"
        elif plano_texto == "Plano Bolsista (Patrocinado)":
            plano = "Bolsista - R$0"
        else:
            plano = plano_texto

        data_nasc = self.data_input.date().toString("yyyy-MM-dd")

        is_kid = self.chk_kids.isChecked()

        if not nome:
            AppDialog("Atenção", "Nome obrigatório.", ("OK",), self).exec()
            return

        if len(telefone) < 10:
            AppDialog("Atenção", "Telefone obrigatório.", ("OK",), self).exec()
            return

        if len(cep) != 8:
            AppDialog("Atenção", "CEP obrigatório.", ("OK",), self).exec()
            return

        if not endereco:
            AppDialog("Atenção", "Endereço obrigatório.", ("OK",), self).exec()
            return

        data_atual = QDate.currentDate()
        if self.data_input.date() > data_atual:
            AppDialog("Atenção", "Data de nascimento inválida.", ("OK",), self).exec()
            return

        if not faixa:
            AppDialog("Atenção", "Faixa obrigatória.", ("OK",), self).exec()
            return

        if not plano:
            AppDialog("Atenção", "Plano obrigatório.", ("OK",), self).exec()
            return

        # ===== KIDS =====
        if is_kid:
            resp_nome = self.resp_nome.text().strip()
            resp_cpf = "".join(filter(str.isdigit, self.resp_cpf.text()))

            if not resp_nome or len(resp_cpf) != 11:
                AppDialog("Atenção", "Dados do responsável obrigatórios.", ("OK",), self).exec()
                return

            if cpf and cpf_kid_existe(cpf):
                AppDialog("Erro", "CPF do aluno já cadastrado (Kids).", ("OK",), self).exec()
                return

            vincular_responsavel = False

            # se responsável já existir, perguntar se deseja vincular
            if cpf_existe(resp_cpf):
                dlg = AppDialog(
                    "Responsável já cadastrado",
                    "Este CPF de responsável já possui cadastro.\n\n"
                    "Deseja vincular este aluno a esse responsável?",
                    ("Não vincular", "Vincular"),
                    self
                )
                dlg.exec()

                if dlg.clicked == "Vincular":
                    vincular_responsavel = True


    # se vinculou, plano fica controlado pelo responsável
            if vincular_responsavel:
                plano_final = "Vinculado ao responsável"
            else:
                plano_final = plano  # usa Kids / Personalizado / Bolsista

            if self.confirmar_salvamento() != "Confirmar":
                return

            # Converter biometria para JSON se existir
            import json
            biometria_json = json.dumps(self.biometria_data) if self.biometria_data else None
            
            inserir_kid(
                nome, cpf, resp_nome, resp_cpf, email,
                telefone, cep, endereco,
                data_nasc, faixa, grau, peso, altura,
                plano_final, self.foto_path, self.certificado_path,
                biometria_json
            )



        # ===== ADULTO =====
        else:
            if not cpf or len(cpf) != 11:
                AppDialog("Atenção", "CPF inválido.", ("OK",), self).exec()
                return

            if cpf_existe(cpf):
                AppDialog("Erro", "CPF já cadastrado.", ("OK",), self).exec()
                return

            if email and email_existe(email):
                AppDialog("Erro", "E-mail já cadastrado.", ("OK",), self).exec()
                return
            
            if self.confirmar_salvamento() != "Confirmar":
                return

            # Converter biometria para JSON se existir
            import json
            biometria_json = json.dumps(self.biometria_data) if self.biometria_data else None
            
            inserir_aluno(
                nome, cpf, email, telefone, cep,
                endereco, data_nasc, faixa, grau, peso, altura,
                plano, self.foto_path, self.certificado_path, 
                biometria_json
            )

        AppDialog("Sucesso", "Cadastro realizado com sucesso!", ("OK",), self).exec()
        self.limpar_formulario()

        if self.refresh_callback:
            self.refresh_callback()
