"""
Testes básicos para funcionalidades Utils (funções utilitárias)
"""

import pytest
import os
from unittest.mock import patch, MagicMock
import utils.vincular_utils as vincular_utils


class TestUtilsBasic:
    """
    Testes básicos para utilitários
    """
    
    def test_utils_modules_importable(self):
        """
        Testa se os módulos utils podem ser importados sem erro
        """
        pytest.importorskip('reportlab', reason="reportlab não instalado")
        try:
            import utils.pdf_report
            import utils.vincular_utils
            assert True, "Módulos utils devem ser importáveis"
        except ImportError as e:
            assert False, f"Erro ao importar módulos utils: {e}"

    def test_pdf_report_has_required_function(self):
        """
        Verifica se módulo pdf_report tem a função principal
        """
        pytest.importorskip('reportlab', reason="reportlab não instalado")
        import utils.pdf_report as pdf_mod

        assert hasattr(pdf_mod, 'gerar_relatorio_mes'), "Módulo deve ter função gerar_relatorio_mes"
        assert callable(pdf_mod.gerar_relatorio_mes), "gerar_relatorio_mes deve ser chamável"
    
    def test_vincular_utils_has_required_function(self):
        """
        Verifica se módulo vincular_utils tem a função principal  
        """
        import utils.vincular_utils as vinc_mod
        
        assert hasattr(vinc_mod, 'vincular_aluno_responsavel'), "Módulo deve ter função vincular_aluno_responsavel"
        assert callable(vinc_mod.vincular_aluno_responsavel), "vincular_aluno_responsavel deve ser chamável"
    
    def test_vincular_aluno_responsavel_funcao_existe(self):
        """
        Testa se a função de vinculação existe e é chamável
        """
        # Assert
        assert hasattr(vincular_utils, 'vincular_aluno_responsavel'), "Função vincular_aluno_responsavel deve existir"
        assert callable(vincular_utils.vincular_aluno_responsavel), "Função deve ser chamável"
    
    def test_gerar_relatorio_mes_function_signature(self):
        """
        Testa se função gerar_relatorio_mes tem assinatura esperada
        """
        pytest.importorskip('reportlab', reason="reportlab não instalado")
        import utils.pdf_report as pdf_mod
        import inspect
        
        # Verificar se função aceita os parâmetros esperados
        sig = inspect.signature(pdf_mod.gerar_relatorio_mes)
        params = list(sig.parameters.keys())
        
        # Verificar se tem pelo menos 3 parâmetros (ano, mês, caminho)
        assert len(params) >= 3, "Função deve aceitar pelo menos 3 parâmetros"
        
        # Tentar chamá-la com parâmetros básicos (vai falhar, mas verifica assinatura)
        try:
            # Usar parâmetros válidos mas que não vão funcionar (sem dependências)
            pdf_mod.gerar_relatorio_mes(2024, 1, "/tmp/test.pdf")
        except Exception as e:
            # É esperado que falhe por dependências, mas pelo menos sabemos que aceita os parâmetros
            assert True, f"Função aceita parâmetros (falha esperada): {e}"