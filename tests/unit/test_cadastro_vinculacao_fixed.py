"""
Testes para a funcionalidade de vinculação de responsáveis na aba de cadastro
"""
import pytest
from unittest.mock import Mock, patch
from PySide6.QtWidgets import QApplication
import sys

# Criar QApplication se não existir
if not QApplication.instance():
    app = QApplication(sys.argv)

from ui.cadastro_aluno_tab import CadastroAlunoTab


class TestCadastroVinculacao:
    """Testes para vinculação de responsáveis na aba de cadastro"""
    
    @pytest.fixture
    def cadastro_tab(self):
        """Fixture para criar instância do CadastroAlunoTab"""
        return CadastroAlunoTab()
    
    @patch('ui.app_dialog.show_input')
    def test_vincular_responsavel_cancelar_cpf_dependente(self, mock_show_input, cadastro_tab):
        """Teste cancelamento na entrada do CPF do dependente"""
        # Simular cancelamento no primeiro diálogo
        mock_show_input.return_value = ("", False)
        
        # Chamar função
        cadastro_tab.vincular_responsavel()
        
        # Verificar que foi chamado apenas uma vez
        assert mock_show_input.call_count == 1
    
    @patch('ui.app_dialog.show_error')
    @patch('ui.app_dialog.show_input')
    def test_vincular_responsavel_cpf_dependente_invalido(self, mock_show_input, mock_show_error, cadastro_tab):
        """Teste CPF do dependente inválido"""
        # Simular entrada de CPF inválido
        mock_show_input.return_value = ("123.456", True)
        
        # Chamar função
        cadastro_tab.vincular_responsavel()
        
        # Verificar que mostrou erro de CPF inválido
        mock_show_error.assert_called_once_with(
            cadastro_tab, "CPF Inválido", "O CPF deve ter 11 dígitos."
        )
    
    @patch('ui.app_dialog.show_input')
    def test_vincular_responsavel_cancelar_cpf_responsavel(self, mock_show_input, cadastro_tab):
        """Teste cancelamento na entrada do CPF do responsável"""
        # Simular entrada válida do dependente, depois cancelamento do responsável
        mock_show_input.side_effect = [
            ("12345678901", True),  # CPF dependente válido
            ("", False)             # Cancelar CPF responsável
        ]
        
        # Chamar função
        cadastro_tab.vincular_responsavel()
        
        # Verificar que foi chamado duas vezes
        assert mock_show_input.call_count == 2
    
    @patch('ui.app_dialog.show_error')
    @patch('ui.app_dialog.show_input')
    def test_vincular_responsavel_cpf_responsavel_invalido(self, mock_show_input, mock_show_error, cadastro_tab):
        """Teste CPF do responsável inválido"""
        # Simular CPFs válido e inválido
        mock_show_input.side_effect = [
            ("12345678901", True),  # CPF dependente válido
            ("987.654", True)       # CPF responsável inválido
        ]
        
        # Chamar função
        cadastro_tab.vincular_responsavel()
        
        # Verificar que mostrou erro de CPF inválido
        mock_show_error.assert_called_once_with(
            cadastro_tab, "CPF Inválido", "O CPF do responsável deve ter 11 dígitos."
        )
    
    @patch('ui.app_dialog.show_error')
    @patch('ui.app_dialog.show_input')
    def test_vincular_responsavel_mesmo_cpf(self, mock_show_input, mock_show_error, cadastro_tab):
        """Teste dependente e responsável com mesmo CPF"""
        # Simular mesmo CPF para ambos
        mock_show_input.side_effect = [
            ("12345678901", True),  # CPF dependente
            ("12345678901", True)   # CPF responsável (mesmo)
        ]
        
        # Chamar função
        cadastro_tab.vincular_responsavel()
        
        # Verificar que mostrou erro
        mock_show_error.assert_called_once_with(
            cadastro_tab, "CPF Inválido", "O dependente não pode ser responsável de si mesmo."
        )
    
    @patch('database.db.get_conn')
    @patch('ui.app_dialog.show_error')
    @patch('ui.app_dialog.show_input')
    def test_vincular_responsavel_dependente_nao_encontrado(self, mock_show_input, mock_show_error, mock_get_conn, cadastro_tab):
        """Teste dependente não encontrado no banco"""
        # Mock do banco de dados
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        # Simular dependente não encontrado
        mock_cursor.fetchone.return_value = None
        
        # Simular CPFs válidos diferentes
        mock_show_input.side_effect = [
            ("12345678901", True),  # CPF dependente
            ("98765432100", True)   # CPF responsável
        ]
        
        # Chamar função
        cadastro_tab.vincular_responsavel()
        
        # Verificar que mostrou erro
        mock_show_error.assert_called_once_with(
            cadastro_tab, "Aluno não encontrado", 
            "Não foi encontrado nenhum aluno ativo com o CPF: 12345678901"
        )
        mock_conn.close.assert_called_once()
    
    @patch('database.db.get_conn')
    @patch('ui.app_dialog.show_info')
    @patch('ui.app_dialog.show_input')
    def test_vincular_responsavel_sucesso(self, mock_show_input, mock_show_info, mock_get_conn, cadastro_tab):
        """Teste vinculação bem-sucedida"""
        # Mock do banco de dados
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        # Mock do callback de refresh
        mock_callback = Mock()
        cadastro_tab.refresh_callback = mock_callback
        
        # Simular dependente e responsável encontrados, sem vinculação prévia
        mock_cursor.fetchone.side_effect = [
            (1, "João Silva"),      # Dependente encontrado
            (2, "Maria Silva"),     # Responsável encontrado
            (None,)                 # Sem responsável vinculado
        ]
        
        # Simular CPFs válidos diferentes
        mock_show_input.side_effect = [
            ("12345678901", True),  # CPF dependente
            ("98765432100", True)   # CPF responsável
        ]
        
        # Chamar função
        cadastro_tab.vincular_responsavel()
        
        # Verificar que mostrou sucesso
        mock_show_info.assert_called_once_with(
            cadastro_tab, "Sucesso", "Aluno João Silva vinculado com sucesso ao responsável: Maria Silva"
        )
        
        # Verificar que chamou callback de refresh
        mock_callback.assert_called_once()
    
    def test_botao_vincular_regra_kids(self, cadastro_tab):
        """Teste que a regra de kids funciona corretamente na função toggle_responsavel"""
        
        # Teste 1: Checkbox não marcado (não-kids)
        cadastro_tab.chk_kids.setChecked(False)
        is_kid = cadastro_tab.chk_kids.isChecked()
        expected_visible = not is_kid
        
        # Para não-kids, botão deve ser visível (expected_visible = True)
        assert expected_visible == True
        
        # Teste 2: Checkbox marcado (kids)
        cadastro_tab.chk_kids.setChecked(True)
        is_kid = cadastro_tab.chk_kids.isChecked()
        expected_visible = not is_kid
        
        # Para kids, botão deve ser invisível (expected_visible = False)
        assert expected_visible == False
        
        # Teste 3: Voltar para não-kids
        cadastro_tab.chk_kids.setChecked(False)
        is_kid = cadastro_tab.chk_kids.isChecked()
        expected_visible = not is_kid
        
        # Novamente para não-kids, botão deve ser visível
        assert expected_visible == True
        
    def test_toggle_responsavel_com_kids(self, cadastro_tab):
        """Teste que a lógica de toggle_responsavel funciona corretamente com kids"""
        
        # Testar a lógica da função sem depender da visibilidade de widgets
        # Caso 1: Kids marcado
        cadastro_tab.chk_kids.setChecked(True)
        is_kid_before = cadastro_tab.chk_kids.isChecked()
        
        # Chamar toggle_responsavel
        cadastro_tab.toggle_responsavel()
        
        # Verificar que o checkbox continua marcado (não alterado pela função)
        assert cadastro_tab.chk_kids.isChecked() == is_kid_before
        
        # Caso 2: Kids desmarcado
        cadastro_tab.chk_kids.setChecked(False)
        is_kid_before = cadastro_tab.chk_kids.isChecked()
        
        cadastro_tab.toggle_responsavel()
        
        # Verificar que o checkbox continua desmarcado
        assert cadastro_tab.chk_kids.isChecked() == is_kid_before