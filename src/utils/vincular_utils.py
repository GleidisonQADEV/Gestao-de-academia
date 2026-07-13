"""
Utilidades para vinculação de alunos - evita duplicação de código
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QListWidget, QListWidgetItem, QPushButton, QFrame
)
from PySide6.QtCore import Qt


def _formatar_cpf(cpf):
    d = "".join(filter(str.isdigit, cpf or ""))
    if len(d) == 11:
        return f"{d[:3]}.{d[3:6]}.{d[6:9]}-{d[9:]}"
    return cpf or ""


class SelecionarResponsavelDialog(QDialog):
    """Diálogo para escolher o responsável com busca por nome ou CPF."""

    def __init__(self, parent, candidatos, titulo="Selecionar responsável"):
        super().__init__(parent)
        self._candidatos = candidatos  # list[(id, nome, cpf)]
        self.selecionado = None        # (id, nome, cpf)
        self.setWindowTitle(titulo)
        self.setModal(True)
        self.setMinimumWidth(460)
        self.setObjectName("selResp")
        self.setStyleSheet("#selResp { background: #111111; }")
        self._build()
        self._filtrar("")

    def _build(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(20, 20, 20, 20)
        main.setSpacing(14)

        card = QFrame()
        card.setStyleSheet("background:#161616; border:1px solid #222222; border-radius:10px;")
        lay = QVBoxLayout(card)
        lay.setContentsMargins(20, 18, 20, 18)
        lay.setSpacing(12)

        titulo = QLabel("Vincular ao responsável")
        titulo.setStyleSheet("color:#ffffff; font-size:15px; font-weight:700; background:transparent; border:none;")
        lay.addWidget(titulo)

        dica = QLabel("Busque pelo nome ou CPF do responsável:")
        dica.setStyleSheet("color:#9a9a9a; font-size:12px; background:transparent; border:none;")
        lay.addWidget(dica)

        self.busca = QLineEdit()
        self.busca.setPlaceholderText("Nome ou CPF...")
        self.busca.setClearButtonEnabled(True)
        self.busca.setStyleSheet(
            "QLineEdit { background:#0e0e0e; padding:8px 12px; border-radius:8px;"
            " border:1px solid #1e1e1e; font-size:13px; color:#ffffff; }"
            "QLineEdit:focus { border:1.5px solid #cc1e1e; }"
        )
        self.busca.textChanged.connect(self._filtrar)
        lay.addWidget(self.busca)

        self.lista = QListWidget()
        self.lista.setStyleSheet(
            "QListWidget { background:#0e0e0e; border:1px solid #1e1e1e; border-radius:8px;"
            " color:#cccccc; font-size:13px; outline:none; }"
            "QListWidget::item { padding:8px 10px; border-radius:5px; }"
            "QListWidget::item:selected { background:#cc1e1e; color:white; }"
        )
        self.lista.setMinimumHeight(220)
        self.lista.itemDoubleClicked.connect(lambda _i: self._confirmar())
        lay.addWidget(self.lista)

        botoes = QHBoxLayout()
        botoes.addStretch()
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setFixedHeight(36)
        btn_cancelar.setCursor(Qt.PointingHandCursor)
        btn_cancelar.setStyleSheet(
            "QPushButton { background:#1e1e1e; color:#cccccc; border:1px solid #2a2a2a;"
            " border-radius:7px; font-size:12px; font-weight:600; padding:0 18px; }"
            "QPushButton:hover { background:#252525; color:#ffffff; }"
        )
        btn_cancelar.clicked.connect(self.reject)
        botoes.addWidget(btn_cancelar)

        btn_ok = QPushButton("Vincular")
        btn_ok.setFixedHeight(36)
        btn_ok.setCursor(Qt.PointingHandCursor)
        btn_ok.setStyleSheet(
            "QPushButton { background:#cc1e1e; color:#ffffff; border:none;"
            " border-radius:7px; font-size:12px; font-weight:700; padding:0 22px; }"
            "QPushButton:hover { background:#e02020; }"
        )
        btn_ok.clicked.connect(self._confirmar)
        botoes.addWidget(btn_ok)
        lay.addLayout(botoes)

        main.addWidget(card)

    def _filtrar(self, termo=""):
        termo = (termo or "").strip().lower()
        so_digitos = "".join(filter(str.isdigit, termo))
        self.lista.clear()
        for cid, nome, cpf in self._candidatos:
            nome_l = (nome or "").lower()
            cpf_l = "".join(filter(str.isdigit, cpf or ""))
            casa = (not termo) or (termo in nome_l) or (so_digitos and so_digitos in cpf_l)
            if casa:
                item = QListWidgetItem(f"{nome}   ·   {_formatar_cpf(cpf)}")
                item.setData(Qt.UserRole, (cid, nome, cpf))
                self.lista.addItem(item)

    def _confirmar(self):
        item = self.lista.currentItem()
        if item is None:
            if self.lista.count() == 1:
                item = self.lista.item(0)
            else:
                return
        self.selecionado = item.data(Qt.UserRole)
        self.accept()


def _listar_responsaveis_disponiveis(excluir_id=None):
    """Retorna adultos ativos que podem ser responsáveis (exceto o próprio)."""
    from database.db import get_conn
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, nome, cpf FROM alunos WHERE ativo=1 AND responsavel_id IS NULL")
    linhas = cur.fetchall()
    conn.close()
    return [(cid, nome, cpf) for (cid, nome, cpf) in linhas if cid != excluir_id]


def vincular_dependente(parent_widget, dependente_id, dependente_nome=None):
    """Vincula o aluno (já identificado) a um responsável escolhido por busca.

    - Não pede o CPF do dependente (é o aluno atual em edição).
    - Permite buscar o responsável por nome ou CPF.
    - Apaga o histórico financeiro (mensalidades) do dependente: só o
      responsável fica com valores.
    """
    from ui.app_dialog import show_error, show_warning, show_info
    from database.db import get_conn

    if not dependente_id:
        show_error(parent_widget, "Erro", "Aluno não identificado para vinculação.")
        return False

    candidatos = _listar_responsaveis_disponiveis(excluir_id=dependente_id)
    if not candidatos:
        show_warning(parent_widget, "Sem responsáveis",
                     "Não há outro adulto ativo disponível para ser responsável.")
        return False

    dlg = SelecionarResponsavelDialog(parent_widget, candidatos)
    if dlg.exec() != QDialog.Accepted or not dlg.selecionado:
        return False

    responsavel_id, responsavel_nome, _cpf = dlg.selecionado
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE alunos SET responsavel_id=?, plano=? WHERE id=?",
                    (responsavel_id, "Vinculado ao responsável", dependente_id))
        # Apagar histórico financeiro do dependente (só o responsável fica com valores)
        cur.execute("DELETE FROM mensalidades WHERE aluno_id=?", (dependente_id,))
        conn.commit()
        conn.close()

        nome = dependente_nome or "Aluno"
        show_info(parent_widget, "Sucesso",
                  f"{nome} vinculado(a) ao responsável {responsavel_nome}.\n"
                  f"O histórico financeiro do dependente foi removido.")
        return True
    except Exception as e:
        show_error(parent_widget, "Erro", f"Erro ao vincular responsável: {str(e)}")
        return False


def vincular_aluno_responsavel(parent_widget):
    """Alias para vincular_dependente - compatibilidade com código existente.

    Vincula um aluno (o atual em edição) a um responsável.
    - Não pede CPF do dependente (é o aluno em edição).
    - Permite buscar responsável por nome ou CPF.
    - Apaga histórico financeiro do dependente.
    """
    # Quando chamado de contexto que não tem dependente_id, temos que pedir
    # Mas a nova interface usa vincular_dependente que é a forma correta
    # Esta função mantém compatibilidade com código antigo que chamava ela sem contexto
    from ui.app_dialog import show_error

    show_error(
        parent_widget,
        "Função Descontinuada",
        "Use 'Vincular a Responsável' através da aba de alunos.\n\n"
        "Para vincular um aluno, selecione-o na lista e clique em 'Vincular a Responsável'."
    )
    return False