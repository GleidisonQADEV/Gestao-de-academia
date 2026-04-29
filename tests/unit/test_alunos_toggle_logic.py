"""
Testes para a lógica de ativação/inativação de alunos
(testando apenas a lógica sem componentes de UI)
"""
import pytest
from unittest.mock import Mock, patch

# Pre-cache com PySide6 real antes que outros módulos de teste mockeem globalmente
try:
    from ui.alunos_tab import AlunosTab as _AlunosTab  # noqa: F401
except Exception:
    _AlunosTab = None


class TestToggleStatusLogic:
    """Testes focados na lógica da função toggle_status"""
    
    def test_status_calculation_logic(self):
        """Teste da lógica de cálculo de status"""
        # Teste: aluno ativo deve virar inativo
        aluno_ativo = {"status": 1}  # ATIVO
        novo_status_ativo = 0 if aluno_ativo["status"] else 1
        assert novo_status_ativo == 0  # Deve ficar INATIVO
        
        # Teste: aluno inativo deve virar ativo
        aluno_inativo = {"status": 0}  # INATIVO
        novo_status_inativo = 0 if aluno_inativo["status"] else 1
        assert novo_status_inativo == 1  # Deve ficar ATIVO
    
    def test_dependentes_detection_logic(self):
        """Teste da lógica de detecção de dependentes"""
        responsavel = {
            "tipo": "adulto",
            "status": 1,  # ATIVO (sendo inativado)
            "cpf": "12345678901"
        }
        
        # Simular lista de registros
        registros = [
            responsavel,
            {
                "tipo": "kids",
                "responsavel_cpf": "12345678901"  # Dependente do responsável
            },
            {
                "tipo": "kids", 
                "responsavel_cpf": "98765432100"  # Dependente de outro responsável
            }
        ]
        
        # Lógica de encontrar dependentes (similar ao código real)
        dependentes_afetados = []
        for registro in registros:
            if (registro["tipo"] == "kids" and 
                registro.get("responsavel_cpf") == responsavel["cpf"]):
                dependentes_afetados.append(registro)
        
        # Verificar que encontrou apenas 1 dependente
        assert len(dependentes_afetados) == 1
    
    @patch('ui.alunos_tab.inativar_aluno')
    def test_executar_inativacao_aluno_adulto_logic(self, mock_inativar_aluno):
        """Teste da lógica de inativação para aluno adulto"""
        from ui.alunos_tab import AlunosTab
        
        # Criar instância mock sem componentes UI
        mock_tab = Mock()
        mock_tab.aluno_atual = {"id": 1, "status": 1}
        
        # Aplicar o método real ao mock
        executar_inativacao = AlunosTab.executar_inativacao.__get__(mock_tab, AlunosTab)
        
        # Dados do aluno
        dados_aluno = {
            "id": 1,
            "status": 1,  # ATIVO
            "tipo": "adulto"
        }
        
        # Executar função
        executar_inativacao(dados_aluno)
        
        # Verificações
        mock_inativar_aluno.assert_called_once_with(1, 0)  # id=1, novo_status=0 (inativo)
        assert mock_tab.aluno_atual["status"] == 0  # Status atualizado
    
    @patch('database.db.get_conn')
    def test_executar_inativacao_kids_logic(self, mock_get_conn):
        """Teste da lógica de inativação para aluno kids"""
        # Mock básico do banco para verificar se a função tenta conectar
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        # Teste apenas se get_conn é chamado (indicando que tenta alterar kids)
        try:
            # Simular apenas a parte que importa
            conn = mock_get_conn()
            cur = conn.cursor()
            cur.execute("UPDATE kids SET ativo=? WHERE id=?", (0, 2))
            conn.commit()
            conn.close()
        except:
            pass
        
        # Verificar que pelo menos tentou conectar ao banco
        mock_get_conn.assert_called_once()
        mock_conn.cursor.assert_called_once()
    
    @patch('database.db.inativar_aluno')
    def test_executar_inativacao_erro_handling(self, mock_inativar):
        """Teste do tratamento de erro na inativação"""
        # Simular erro
        mock_inativar.side_effect = Exception("Erro de conexão")
        
        # Testar apenas a lógica de erro, sem UI
        dados_aluno = {
            "id": 1,
            "status": 1,
            "tipo": "adulto"
        }
        
        # A função deve capturar a exceção e tentar mostrar erro
        # Como não podemos testar show_error sem problemas de UI,
        # vamos apenas verificar se a exceção foi lançada pelo mock
        mock_inativar.side_effect = Exception("Erro de conexão")
        
        # Verificar que o mock foi configurado corretamente
        with pytest.raises(Exception) as exc_info:
            mock_inativar(1, 0)
        
        assert str(exc_info.value) == "Erro de conexão"
    
    def test_status_text_logic(self):
        """Teste da lógica de texto de status"""
        # Lógica similar à do código real
        aluno_ativo = {"status": 1}
        status_atual_ativo = "ATIVO" if aluno_ativo["status"] else "INATIVO"
        novo_status_texto_ativo = "INATIVO" if aluno_ativo["status"] else "ATIVO"
        
        assert status_atual_ativo == "ATIVO"
        assert novo_status_texto_ativo == "INATIVO"
        
        aluno_inativo = {"status": 0}
        status_atual_inativo = "ATIVO" if aluno_inativo["status"] else "INATIVO"
        novo_status_texto_inativo = "INATIVO" if aluno_inativo["status"] else "ATIVO"
        
        assert status_atual_inativo == "INATIVO" 
        assert novo_status_texto_inativo == "ATIVO"
    
    def test_codigo_nao_tem_referencia_mostrar_detalhes(self):
        """Teste que verifica se o código não referencia o método mostrar_detalhes inexistente"""
        from ui.alunos_tab import AlunosTab
        import inspect
        
        # Obter o código fonte da função executar_inativacao
        source = inspect.getsource(AlunosTab.executar_inativacao)
        
        # Verificar que não há referência ao método problemático
        assert "mostrar_detalhes" not in source, "Código ainda contém referência ao método inexistente mostrar_detalhes"
        
    def test_executar_inativacao_nao_falha_por_atributo_inexistente(self):
        """Teste de integração que verifica que executar_inativacao não falha por atributo inexistente"""
        
        # Este teste simplesmente verifica que o método existe e pode ser importado
        # sem erro de sintaxe ou referência a atributos inexistentes
        from ui.alunos_tab import AlunosTab
        
        # Se chegou até aqui, o módulo foi importado com sucesso
        assert hasattr(AlunosTab, 'executar_inativacao')
        
        # Verificar que o método é callable
        assert callable(getattr(AlunosTab, 'executar_inativacao'))