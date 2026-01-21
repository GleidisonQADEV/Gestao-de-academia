"""
Configurações globais para testes pytest
"""
import os
import sys
import pytest
import tempfile
import sqlite3
from datetime import datetime, date
from unittest.mock import MagicMock

# Adicionar o diretório src ao path para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

@pytest.fixture
def temp_db():
    """Criar um banco de dados temporário para testes"""
    temp_db_fd, temp_db_path = tempfile.mkstemp(suffix='.db')
    os.close(temp_db_fd)
    
    # Configurar para usar o banco temporário
    from database import db
    from database import kids_db
    original_db_path = db.DB_PATH
    original_kids_db_path = kids_db.DB_PATH
    
    db.DB_PATH = temp_db_path
    kids_db.DB_PATH = temp_db_path
    
    # Inicializar os bancos
    db.init_db()
    kids_db.init_kids_db()
    
    yield temp_db_path
    
    # Cleanup
    db.DB_PATH = original_db_path
    kids_db.DB_PATH = original_kids_db_path
    if os.path.exists(temp_db_path):
        os.unlink(temp_db_path)

@pytest.fixture
def sample_aluno_data():
    """Dados de exemplo para um aluno adulto"""
    return {
        'nome': 'João Silva',
        'cpf': '12345678901',
        'email': 'joao@test.com',
        'telefone': '11999999999',
        'cep': '01234567',
        'endereco': 'Rua Teste, 123',
        'data_nasc': '1990-01-01',
        'faixa': 'Branca',
        'grau': '1',
        'peso': '75',
        'altura': '1.80',
        'plano': 'Mensal',
        'foto_path': None,
        'certificado_path': None,
        'biometria_data': None
    }

@pytest.fixture  
def sample_kid_data():
    """Dados de exemplo para uma criança"""
    return {
        'nome': 'Pedro Silva',
        'cpf': '98765432109',
        'resp_nome': 'João Silva',
        'resp_cpf': '12345678901',
        'email': 'pedro@test.com',
        'telefone': '11888888888',
        'cep': '01234567',
        'endereco': 'Rua Teste, 123',
        'data_nasc': '2015-01-01',
        'faixa': 'Branca',
        'grau': '1',
        'peso': '30',
        'altura': '1.20',
        'plano': 'Mensal',
        'foto_path': None,
        'certificado_path': None,
        'biometria_data': None
    }

@pytest.fixture
def sample_mensalidade_data():
    """Dados de exemplo para mensalidade"""
    return {
        'aluno_id': 1,
        'valor': 150.0,
        'data_vencimento': date.today(),
        'observacoes': 'Teste mensalidade'
    }

@pytest.fixture
def mock_qt_widgets():
    """Mock para widgets Qt durante testes unitários"""
    mock_widgets = MagicMock()
    
    # Simular classes Qt principais
    mock_widgets.QWidget = MagicMock
    mock_widgets.QDialog = MagicMock
    mock_widgets.QLabel = MagicMock
    mock_widgets.QPushButton = MagicMock
    mock_widgets.QLineEdit = MagicMock
    
    return mock_widgets

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Configuração automática para todos os testes"""
    # Garantir que não há interferência com banco real
    test_db_path = os.path.join(tempfile.gettempdir(), 'test_legacy_bjj.db')
    
    # Se existir banco de teste antigo, remover
    if os.path.exists(test_db_path):
        os.unlink(test_db_path)
    
    yield
    
    # Cleanup após testes
    if os.path.exists(test_db_path):
        os.unlink(test_db_path)