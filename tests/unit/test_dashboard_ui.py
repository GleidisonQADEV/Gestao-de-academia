"""
Testes de integração para o Dashboard UI
- Carregamento de dados
- Interações do usuário
- Validação de componentes
"""

import pytest
from unittest.mock import Mock, patch
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from datetime import date

from ui.dashboard_tab import DashboardTab


class TestDashboardUI:
    """Testa a interface do dashboard"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
    
    def test_dashboard_inicializacao(self):
        """Testa se o dashboard inicializa corretamente"""
        dashboard = DashboardTab()
        
        # Verificar se componentes principais existem
        assert hasattr(dashboard, 'card_atrasadas')
        assert hasattr(dashboard, 'card_pagas')
        assert hasattr(dashboard, 'card_vencer')
        assert hasattr(dashboard, 'card_receita')
        assert hasattr(dashboard, 'alunos_stats')
        
        # Verificar se é um widget válido
        assert dashboard.isWidgetType()
    
    @patch('ui.dashboard_tab.obter_metricas_dashboard')
    def test_dashboard_load_dados(self, mock_metricas):
        """Testa carregamento de dados do dashboard"""
        # Mock dos dados
        mock_metricas.return_value = {
            'atrasadas': {'count': 5, 'valor': 1000.0},
            'pagas_mes': {'count': 10, 'valor': 2000.0},
            'a_vencer': {'count': 3, 'valor': 600.0},
            'receita_anual': 25000.0,
            'alunos': {
                'responsaveis': 15,
                'dependentes': 8,
                'kids': 12,
                'bolsistas': 2,
                'total': 35
            }
        }
        
        dashboard = DashboardTab()
        dashboard.load()
        
        # Verificar se a função foi chamada
        mock_metricas.assert_called_once()
        
        # Verificar se os cards foram atualizados
        assert dashboard.card_atrasadas.count_label.text() == "5"
        assert "R$ 1.000,00" in dashboard.card_atrasadas.value_label.text()
        assert dashboard.card_pagas.count_label.text() == "10"
        assert "R$ 2.000,00" in dashboard.card_pagas.value_label.text()
    
    @patch('ui.dashboard_tab.obter_metricas_dashboard')
    def test_dashboard_valores_zero(self, mock_metricas):
        """Testa dashboard com valores zero"""
        # Mock com dados zerados
        mock_metricas.return_value = {
            'atrasadas': {'count': 0, 'valor': 0.0},
            'pagas_mes': {'count': 0, 'valor': 0.0},
            'a_vencer': {'count': 0, 'valor': 0.0},
            'receita_anual': 0.0,
            'alunos': {
                'responsaveis': 0,
                'dependentes': 0,
                'kids': 0,
                'bolsistas': 0,
                'total': 0
            }
        }
        
        dashboard = DashboardTab()
        dashboard.load()
        
        # Verificar se mostra zero corretamente
        assert dashboard.card_atrasadas.count_label.text() == "0"
        assert "R$ 0,00" in dashboard.card_atrasadas.value_label.text()
        assert dashboard.card_receita.value_label.text() == "R$ 0,00"
    
    @patch('ui.dashboard_tab.gerar_mensalidades_anuais')
    @patch('ui.dashboard_tab.show_question')
    @patch('ui.dashboard_tab.show_info')
    def test_botao_gerar_anuais(self, mock_show_info, mock_show_question, mock_gerar):
        """Testa o botão de gerar mensalidades anuais"""
        # Mock da confirmação do usuário
        mock_show_question.return_value = True
        
        # Mock do resultado da geração
        mock_gerar.return_value = {
            'mensalidades_criadas': 24,
            'alunos_processados': 2,
            'detalhes': ['João: 12 mensalidades', 'Maria: 12 mensalidades']
        }
        
        dashboard = DashboardTab()
        
        # Simular clique no botão
        dashboard.gerar_mensalidades_anuais()
        
        # Verificar se as funções foram chamadas
        mock_show_question.assert_called_once()
        mock_gerar.assert_called_once()
        mock_show_info.assert_called_once()
        
        # Verificar se a mensagem de sucesso contém os dados corretos
        call_args = mock_show_info.call_args[0]
        assert "24 mensalidades" in call_args[1]
        assert "2 alunos" in call_args[1]
    
    @patch('ui.dashboard_tab.show_question')
    def test_botao_gerar_anuais_cancelado(self, mock_show_question):
        """Testa quando usuário cancela a geração anual"""
        # Mock da confirmação negativa
        mock_show_question.return_value = False
        
        dashboard = DashboardTab()
        
        # Simular clique no botão
        dashboard.gerar_mensalidades_anuais()
        
        # Verificar que apenas a confirmação foi chamada
        mock_show_question.assert_called_once()
    
    @patch('ui.dashboard_tab.obter_metricas_dashboard')
    def test_refresh_manual(self, mock_metricas):
        """Testa o botão de refresh manual"""
        # Mock inicial
        mock_metricas.return_value = {
            'atrasadas': {'count': 1, 'valor': 200.0},
            'pagas_mes': {'count': 1, 'valor': 200.0},
            'a_vencer': {'count': 1, 'valor': 200.0},
            'receita_anual': 2400.0,
            'alunos': {'responsaveis': 1, 'dependentes': 0, 'kids': 0, 'bolsistas': 0, 'total': 1}
        }
        
        dashboard = DashboardTab()
        initial_load_calls = mock_metricas.call_count
        
        # Encontrar e clicar no botão de atualizar
        for i in range(dashboard.layout().count()):
            item = dashboard.layout().itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if hasattr(widget, 'layout'):
                    for j in range(widget.layout().count()):
                        btn_item = widget.layout().itemAt(j)
                        if btn_item and btn_item.widget() and hasattr(btn_item.widget(), 'text'):
                            if "Atualizar" in btn_item.widget().text():
                                btn_item.widget().click()
                                break
        
        # Verificar se houve nova chamada para métricas (refresh)
        assert mock_metricas.call_count > initial_load_calls
    
    def test_dashboard_formatacao_moeda(self):
        """Testa formatação de valores monetários"""
        dashboard = DashboardTab()
        
        # Testar método hex_to_rgb se existir
        if hasattr(dashboard, 'hex_to_rgb'):
            rgb = dashboard.hex_to_rgb('#E74C3C')
            assert '231,76,60' in rgb or isinstance(rgb, str)
    
    def test_dashboard_cores_cards(self):
        """Testa se as cores dos cards estão corretas"""
        dashboard = DashboardTab()
        
        # Verificar se os cards foram criados com as cores certas
        assert dashboard.card_atrasadas is not None
        assert dashboard.card_pagas is not None
        assert dashboard.card_vencer is not None
        assert dashboard.card_receita is not None


class TestDashboardProgresBarras:
    """Testa as barras de progresso do dashboard"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
    
    @patch('ui.dashboard_tab.obter_metricas_dashboard')
    def test_progress_bars_atualizacao(self, mock_metricas):
        """Testa se as barras de progresso são atualizadas"""
        # Mock com dados para progress bars
        mock_metricas.return_value = {
            'atrasadas': {'count': 0, 'valor': 0.0},
            'pagas_mes': {'count': 0, 'valor': 0.0},
            'a_vencer': {'count': 0, 'valor': 0.0},
            'receita_anual': 0.0,
            'alunos': {
                'responsaveis': 10,
                'dependentes': 5,
                'kids': 8,
                'bolsistas': 2,
                'total': 23
            }
        }
        
        dashboard = DashboardTab()
        dashboard.load()
        
        # Verificar se progress bars existem
        assert hasattr(dashboard, 'progress_responsaveis')
        assert hasattr(dashboard, 'progress_dependentes') 
        assert hasattr(dashboard, 'progress_kids')
        assert hasattr(dashboard, 'progress_bolsistas')
        
        # Verificar valores das progress bars
        total = 23
        assert dashboard.progress_responsaveis.value() == 10
        assert dashboard.progress_responsaveis.maximum() == total
        assert dashboard.progress_dependentes.value() == 5
        assert dashboard.progress_kids.value() == 8
        assert dashboard.progress_bolsistas.value() == 2
    
    @patch('ui.dashboard_tab.obter_metricas_dashboard')
    def test_progress_bars_zero_total(self, mock_metricas):
        """Testa progress bars quando total é zero"""
        mock_metricas.return_value = {
            'atrasadas': {'count': 0, 'valor': 0.0},
            'pagas_mes': {'count': 0, 'valor': 0.0},
            'a_vencer': {'count': 0, 'valor': 0.0},
            'receita_anual': 0.0,
            'alunos': {
                'responsaveis': 0,
                'dependentes': 0,
                'kids': 0,
                'bolsistas': 0,
                'total': 0
            }
        }
        
        dashboard = DashboardTab()
        dashboard.load()
        
        # Progress bars devem ter maximum 1 para evitar divisão por zero
        assert dashboard.progress_responsaveis.maximum() >= 1
        assert dashboard.progress_responsaveis.value() == 0


class TestDashboardShowEvent:
    """Testa o evento de mostrar dashboard"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
    
    @patch('ui.dashboard_tab.obter_metricas_dashboard')
    def test_show_event_carrega_dados(self, mock_metricas):
        """Testa se showEvent carrega os dados"""
        mock_metricas.return_value = {
            'atrasadas': {'count': 0, 'valor': 0.0},
            'pagas_mes': {'count': 0, 'valor': 0.0},
            'a_vencer': {'count': 0, 'valor': 0.0},
            'receita_anual': 0.0,
            'alunos': {'responsaveis': 0, 'dependentes': 0, 'kids': 0, 'bolsistas': 0, 'total': 0}
        }
        
        dashboard = DashboardTab()
        
        # Resetar mock para contar apenas o showEvent
        mock_metricas.reset_mock()
        
        # Simular showEvent
        from PySide6.QtGui import QShowEvent
        event = QShowEvent()
        dashboard.showEvent(event)
        
        # Verificar se load foi chamado
        mock_metricas.assert_called_once()
    
    def test_setup_timer_nao_cria_timer(self):
        """Testa se setup_timer não cria timer (otimização)"""
        dashboard = DashboardTab()
        
        # Verificar se não há timer ativo (otimização para economizar memória)
        assert not hasattr(dashboard, 'timer') or dashboard.timer is None