"""Janela de Ajuda com tutorial de uso e FAQ do sistema."""
from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextBrowser, QPushButton
from PySide6.QtCore import Qt


_CONTEUDO_HTML = """
<h1 style="color:#cc1e1e;">Legacy BJJ — Ajuda</h1>

<h2 style="color:#ffffff;">📘 Tutorial de Uso</h2>

<h3 style="color:#e0e0e0;">1. Login</h3>
<p>Abra o aplicativo e informe usuário e senha. Você pode pressionar
<b>Enter</b> para entrar. O usuário padrão é <b>admin</b> / <b>senha</b>.
Recomendamos trocar a senha em <b>Configurações → Segurança</b>.</p>

<h3 style="color:#e0e0e0;">2. Dashboard</h3>
<p>Tela inicial com os principais indicadores: total de alunos, receita,
distribuição por faixa (incluindo as faixas Kids) e alunos recentes.</p>

<h3 style="color:#e0e0e0;">3. Cadastrar Aluno</h3>
<p>Preencha os dados do aluno (nome, CPF, contato, faixa, plano etc.).
Para crianças, use a opção Kids e informe o responsável. É possível
vincular dependentes a um responsável.</p>

<h3 style="color:#e0e0e0;">4. Alunos</h3>
<p>Lista todos os alunos cadastrados. Use a busca para localizar,
editar ou inativar um aluno.</p>

<h3 style="color:#e0e0e0;">5. Financeiro</h3>
<p>Gerencie mensalidades: valores, vencimentos e pagamentos.</p>

<h3 style="color:#e0e0e0;">6. Importar alunos (Google Sheets)</h3>
<p>Em <b>Configurações → Dados</b>, cole o link de uma planilha do Google
Sheets compartilhada como "qualquer pessoa com o link pode ver". A primeira
linha deve conter os cabeçalhos: <i>nome, cpf, email, telefone, cep, endereco,
data_nascimento, faixa, grau, peso, altura, plano</i>. Apenas <b>nome</b> é
obrigatório e CPFs já cadastrados são ignorados.</p>
<p><b>Importar Kids:</b> use o botão "Importar Kids" para a planilha de menores.
Se o CPF do responsável já for um aluno adulto cadastrado, o Kid é vinculado
automaticamente a ele.</p>
<p style="color:#f2c200;"><b>Ordem recomendada:</b> importe primeiro os
<b>alunos adultos</b> (responsáveis) e só depois os <b>Kids</b> — assim a
vinculação ao responsável acontece automaticamente.</p>

<h3 style="color:#e0e0e0;">7. Exportar PDF</h3>
<p>Em <b>Configurações → Dados</b> você gera relatórios em PDF: financeiro,
lista de alunos e frequência.</p>

<h3 style="color:#e0e0e0;">8. Frequência / Presença</h3>
<p>O percentual de presença é calculado sobre <b>44 aulas por mês</b>
(seg/qua/sex: 3 aulas; ter/qui: 1 aula).</p>

<h3 style="color:#e0e0e0;">9. Atualizações</h3>
<p>Em <b>Configurações → Sistema</b>, clique em <b>Verificar atualizações</b>.
Se houver uma versão nova no GitHub, o app baixa e instala o novo instalador.</p>

<hr>

<h2 style="color:#ffffff;">❓ FAQ — Perguntas Frequentes</h2>

<p><b>Meus dados somem quando fecho o programa?</b><br>
Não. Os dados são gravados em um banco de dados na pasta de dados do usuário
e permanecem entre as execuções.</p>

<p><b>Esqueci a senha, e agora?</b><br>
Na tela de login use <b>"Restaurar Senha Padrão"</b> para voltar a admin / senha.</p>

<p><b>A importação do Google Sheets não funcionou.</b><br>
Verifique se a planilha está compartilhada publicamente (qualquer pessoa com o
link) e se a primeira linha contém os cabeçalhos corretos.</p>

<p><b>Por que a faixa amarela dos Kids aparecia cinza?</b><br>
Isso foi corrigido: o gráfico agora usa as cores corretas das faixas Kids.</p>

<p><b>Como registro presença nos horários de terça e quinta?</b><br>
As aulas de ter/qui são às 12h; seg/qua/sex às 08:30, 17:30 e 18:30.</p>

<p><b>O PDF não abre.</b><br>
O arquivo é salvo no local escolhido. Abra-o com qualquer leitor de PDF.</p>
"""


class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ajuda — Legacy BJJ")
        self.resize(680, 640)
        self.setStyleSheet("QDialog { background: #111111; }")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml(_CONTEUDO_HTML)
        browser.setStyleSheet(
            "QTextBrowser { background: #161616; color: #cfcfcf; border: 1px solid #222222;"
            " border-radius: 8px; padding: 12px; font-size: 13px; }"
        )
        layout.addWidget(browser, 1)

        btn_fechar = QPushButton("Fechar")
        btn_fechar.setCursor(Qt.PointingHandCursor)
        btn_fechar.setFixedHeight(36)
        btn_fechar.setStyleSheet(
            "QPushButton { background: #cc1e1e; color: #ffffff; border: none;"
            " border-radius: 7px; font-size: 13px; font-weight: 600; padding: 0 20px; }"
            " QPushButton:hover { background: #e02020; }"
        )
        btn_fechar.clicked.connect(self.accept)
        layout.addWidget(btn_fechar, 0, Qt.AlignRight)
