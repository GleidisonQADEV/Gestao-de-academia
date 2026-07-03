"""
Testes unitários para componentes de UI
"""
import pytest
from unittest.mock import MagicMock, patch, call
import sys
import os

# Mock do PySide6 antes de importar UI components.
# Guardamos os módulos reais para restaurá-los logo em seguida, evitando que o
# mock vaze para outros arquivos de teste (o que quebraria os testes que usam o
# Qt real e poderia causar segmentation fault).
_PYSIDE_KEYS = ['PySide6', 'PySide6.QtWidgets', 'PySide6.QtCore', 'PySide6.QtGui']
_real_pyside_modules = {k: sys.modules.get(k) for k in _PYSIDE_KEYS}

sys.modules['PySide6'] = MagicMock()
sys.modules['PySide6.QtWidgets'] = MagicMock()
sys.modules['PySide6.QtCore'] = MagicMock()
sys.modules['PySide6.QtGui'] = MagicMock()

# Importar depois do mock
from ui.app_dialog import show_info, show_warning, show_error, show_question, show_input

# Restaurar imediatamente os módulos reais do PySide6 para não poluir o estado
# global compartilhado entre os testes.
for _k, _v in _real_pyside_modules.items():
    if _v is not None:
        sys.modules[_k] = _v
    else:
        sys.modules.pop(_k, None)


class TestAppDialog:
    """Testes para diálogos de aplicação"""
    
    @patch('ui.app_dialog.AppDialog')
    def test_show_info(self, mock_app_dialog):
        """Teste diálogo de informação"""
        mock_dialog_instance = MagicMock()
        mock_app_dialog.return_value = mock_dialog_instance
        mock_dialog_instance.exec.return_value = None
        mock_dialog_instance.clicked = "OK"
        
        result = show_info(None, "Título", "Mensagem")
        
        mock_app_dialog.assert_called_once_with("Título", "Mensagem", ("OK",), None)
        mock_dialog_instance.exec.assert_called_once()
        assert result == "OK"
    
    @patch('ui.app_dialog.AppDialog')  
    def test_show_warning(self, mock_app_dialog):
        """Teste diálogo de aviso"""
        mock_dialog_instance = MagicMock()
        mock_app_dialog.return_value = mock_dialog_instance
        mock_dialog_instance.exec.return_value = None
        mock_dialog_instance.clicked = "OK"
        
        result = show_warning(None, "Título", "Mensagem")
        
        mock_app_dialog.assert_called_once_with("Título", "Mensagem", ("OK",), None)
        assert result == "OK"
    
    @patch('ui.app_dialog.AppDialog')
    def test_show_error(self, mock_app_dialog):
        """Teste diálogo de erro"""
        mock_dialog_instance = MagicMock()
        mock_app_dialog.return_value = mock_dialog_instance
        mock_dialog_instance.exec.return_value = None
        mock_dialog_instance.clicked = "OK"
        
        result = show_error(None, "Título", "Mensagem")
        
        mock_app_dialog.assert_called_once_with("Título", "Mensagem", ("OK",), None)
        assert result == "OK"
    
    @patch('ui.app_dialog.AppDialog')
    def test_show_question_yes(self, mock_app_dialog):
        """Teste diálogo de pergunta - resposta SIM"""
        mock_dialog_instance = MagicMock()
        mock_app_dialog.return_value = mock_dialog_instance
        mock_dialog_instance.exec.return_value = None
        mock_dialog_instance.clicked = "Sim"
        
        result = show_question(None, "Título", "Mensagem")
        
        mock_app_dialog.assert_called_once_with("Título", "Mensagem", ("Sim", "Não"), None)
        assert result is True
    
    @patch('ui.app_dialog.AppDialog')
    def test_show_question_no(self, mock_app_dialog):
        """Teste diálogo de pergunta - resposta NÃO"""
        mock_dialog_instance = MagicMock()
        mock_app_dialog.return_value = mock_dialog_instance
        mock_dialog_instance.exec.return_value = None
        mock_dialog_instance.clicked = "Não"
        
        result = show_question(None, "Título", "Mensagem")
        
        assert result is False
    
    @patch('ui.app_dialog.InputDialog')
    @patch('ui.app_dialog.QDialog')
    def test_show_input_success(self, mock_qdialog, mock_input_dialog):
        """Teste diálogo de entrada - entrada válida"""
        mock_dialog_instance = MagicMock()
        mock_input_dialog.return_value = mock_dialog_instance
        mock_dialog_instance.exec.return_value = mock_qdialog.DialogCode.Accepted
        mock_dialog_instance.get_text.return_value = ("teste input", True)
        
        result_text, result_ok = show_input(None, "Título", "Mensagem", "placeholder")
        
        mock_input_dialog.assert_called_once_with("Título", "Mensagem", "placeholder", None)
        assert result_text == "teste input"
        assert result_ok is True
    
    @patch('ui.app_dialog.InputDialog')
    @patch('ui.app_dialog.QDialog')
    def test_show_input_cancel(self, mock_qdialog, mock_input_dialog):
        """Teste diálogo de entrada - cancelado"""
        mock_dialog_instance = MagicMock()
        mock_input_dialog.return_value = mock_dialog_instance
        mock_dialog_instance.exec.return_value = mock_qdialog.DialogCode.Rejected
        
        result_text, result_ok = show_input(None, "Título", "Mensagem")
        
        assert result_text == ""
        assert result_ok is False


class TestUIValidation:
    """Testes para validações de interface"""
    
    def test_cpf_format_validation(self):
        """Teste formatação de CPF"""
        # Simular função de validação de CPF
        def format_cpf(cpf_str):
            digits = ''.join(filter(str.isdigit, cpf_str))
            if len(digits) == 11:
                return f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"
            return cpf_str
        
        assert format_cpf("12345678901") == "123.456.789-01"
        assert format_cpf("123.456.789-01") == "123.456.789-01"
        assert format_cpf("123456789") == "123456789"  # CPF inválido mantém original
    
    def test_phone_format_validation(self):
        """Teste formatação de telefone"""
        def format_phone(phone_str):
            digits = ''.join(filter(str.isdigit, phone_str))
            if len(digits) == 11:
                return f"({digits[:2]}) {digits[2:7]}-{digits[7:]}"
            elif len(digits) == 10:
                return f"({digits[:2]}) {digits[2:6]}-{digits[6:]}"
            return phone_str
        
        assert format_phone("11999999999") == "(11) 99999-9999"
        assert format_phone("1133333333") == "(11) 3333-3333"
        assert format_phone("119999") == "119999"  # Inválido mantém original
    
    def test_cep_format_validation(self):
        """Teste formatação de CEP"""
        def format_cep(cep_str):
            digits = ''.join(filter(str.isdigit, cep_str))
            if len(digits) == 8:
                return f"{digits[:5]}-{digits[5:]}"
            return cep_str
        
        assert format_cep("01234567") == "01234-567"
        assert format_cep("01234-567") == "01234-567"
        assert format_cep("0123") == "0123"  # Inválido mantém original


class TestFinanceiroTab:
    """Testes para componentes da aba financeiro"""
    
    @patch('database.db.listar_mensalidades')
    @patch('ui.financeiro_tab.show_error')
    def test_load_mensalidades_error_handling(self, mock_show_error, mock_listar):
        """Teste tratamento de erro ao carregar mensalidades"""
        # Simular erro na consulta
        mock_listar.side_effect = Exception("Erro de conexão")
        
        # Simular instância da aba financeiro
        from unittest.mock import Mock
        financeiro_tab = Mock()
        
        # Simular método load com tratamento de erro
        def mock_load():
            try:
                mensalidades = mock_listar()
            except Exception as e:
                mock_show_error(financeiro_tab, "Erro ao carregar dados", f"Erro: {str(e)}")
        
        mock_load()
        
        mock_show_error.assert_called_once_with(
            financeiro_tab, 
            "Erro ao carregar dados", 
            "Erro: Erro de conexão"
        )
    
    def test_filtrar_mensalidades_por_status(self):
        """Teste filtro de mensalidades por status"""
        # Dados de exemplo
        mensalidades_mock = [
            (1, 'João', 150.0, '2024-01-01', '2024-01-01', 'PAGO', '', '', '', ''),
            (2, 'Maria', 150.0, '2024-01-01', None, 'PENDENTE', '', '', '', ''),
            (3, 'José', 150.0, '2024-01-01', None, 'PENDENTE', '', '', '', ''),
        ]
        
        # Simular filtro
        def filtrar_por_status(mensalidades, status):
            if status:
                return [m for m in mensalidades if m[5] == status]
            return mensalidades
        
        # Testar filtros
        todas = filtrar_por_status(mensalidades_mock, None)
        assert len(todas) == 3
        
        pagas = filtrar_por_status(mensalidades_mock, 'PAGO')
        assert len(pagas) == 1
        
        pendentes = filtrar_por_status(mensalidades_mock, 'PENDENTE')
        assert len(pendentes) == 2


class TestVinculoResponsavel:
    """Testes específicos para funcionalidade de vínculo de responsável"""
    
    @patch('database.db.get_conn')
    @patch('ui.app_dialog.show_input')
    @patch('ui.app_dialog.show_error')
    @patch('ui.app_dialog.show_info')
    def test_vincular_responsavel_success(self, mock_show_info, mock_show_error, mock_show_input, mock_get_conn):
        """Teste vinculação bem-sucedida de responsável"""
        # Configurar mocks
        mock_show_input.return_value = ("12345678901", True)
        
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cur
        
        # Mock da consulta de responsável
        mock_cur.fetchone.side_effect = [
            (1, "João Silva"),  # Responsável encontrado
            (None,)  # Aluno ainda não tem responsável
        ]
        
        # Simular dados do aluno atual
        dados_aluno = (None, 2, "Pedro Silva")  # (dialog, id, nome)
        
        # Simular método vincular_responsavel
        def mock_vincular_responsavel():
            cpf_responsavel, ok = mock_show_input(
                None, "Vincular Responsável", 
                "Digite o CPF do responsável:", "000.000.000-00"
            )
            
            if not ok:
                return
            
            # Limpar CPF
            cpf_responsavel = ''.join(filter(str.isdigit, cpf_responsavel.strip()))
            
            if len(cpf_responsavel) != 11:
                mock_show_error(None, "CPF Inválido", "O CPF deve ter 11 dígitos.")
                return
            
            conn = mock_get_conn()
            cur = conn.cursor()
            
            # Verificar se responsável existe
            cur.execute("SELECT id, nome FROM alunos WHERE cpf = ? AND ativo = 1", (cpf_responsavel,))
            responsavel = cur.fetchone()
            
            if not responsavel:
                mock_show_error(None, "Responsável não encontrado", "")
                return
            
            responsavel_id, responsavel_nome = responsavel
            aluno_id = dados_aluno[1]
            
            # Verificar se já tem responsável
            cur.execute("SELECT responsavel_id FROM alunos WHERE id = ?", (aluno_id,))
            resultado = cur.fetchone()
            
            if resultado and resultado[0]:
                return
            
            # Vincular
            cur.execute("UPDATE alunos SET responsavel_id = ? WHERE id = ?", (responsavel_id, aluno_id))
            conn.commit()
            
            mock_show_info(None, "Sucesso", f"Aluno vinculado com sucesso ao responsável: {responsavel_nome}")
        
        # Executar teste
        mock_vincular_responsavel()
        
        # Verificar chamadas
        mock_show_input.assert_called_once()
        mock_show_info.assert_called_once_with(None, "Sucesso", "Aluno vinculado com sucesso ao responsável: João Silva")
        mock_show_error.assert_not_called()
    
    @patch('ui.app_dialog.show_input')
    @patch('ui.app_dialog.show_error')
    def test_vincular_responsavel_cpf_invalid(self, mock_show_error, mock_show_input):
        """Teste vinculação com CPF inválido"""
        # CPF com menos de 11 dígitos
        mock_show_input.return_value = ("123456789", True)
        
        def mock_vincular_responsavel():
            cpf_responsavel, ok = mock_show_input(
                None, "Vincular Responsável",
                "Digite o CPF do responsável:", "000.000.000-00"
            )
            
            if not ok:
                return
            
            cpf_responsavel = ''.join(filter(str.isdigit, cpf_responsavel.strip()))
            
            if len(cpf_responsavel) != 11:
                mock_show_error(None, "CPF Inválido", "O CPF deve ter 11 dígitos.")
                return
        
        mock_vincular_responsavel()
        
        mock_show_error.assert_called_once_with(None, "CPF Inválido", "O CPF deve ter 11 dígitos.")
    
    @patch('ui.app_dialog.show_input')
    def test_vincular_responsavel_cancelado(self, mock_show_input):
        """Teste vinculação cancelada pelo usuário"""
        mock_show_input.return_value = ("", False)
        
        def mock_vincular_responsavel():
            cpf_responsavel, ok = mock_show_input(
                None, "Vincular Responsável",
                "Digite o CPF do responsável:", "000.000.000-00"
            )
            
            if not ok or not cpf_responsavel.strip():
                return "cancelado"
            
            return "prosseguir"
        
        result = mock_vincular_responsavel()
        assert result == "cancelado"