"""
Testes básicos para funcionalidades críticas de autenticação e inicialização
"""

import pytest
import os
import tempfile
import sqlite3
import database.db as db


class TestAuthAndInit:
    """
    Testes básicos para funções críticas de autenticação e inicialização
    """

    def setup_method(self):
        """Setup para cada teste"""
        # Usar banco temporário para testes
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        self.temp_db.close()
        
        # Mock do caminho do DB
        self.original_db_path = db.DB_PATH
        db.DB_PATH = self.temp_db.name
    
    def teardown_method(self):
        """Cleanup após cada teste"""
        # Restaurar caminho original
        db.DB_PATH = self.original_db_path
        
        # Remover arquivo temporário
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)

    def test_init_db_creates_tables_successfully(self):
        """
        Testa se init_db cria todas as tabelas necessárias
        """
        # Act
        db.init_db()
        
        # Assert - Verificar se as tabelas foram criadas
        conn = db.get_conn()
        cursor = conn.cursor()
        
        # Verificar tabela users
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        users_table = cursor.fetchone()
        assert users_table is not None, "Tabela users deve ser criada"
        
        # Verificar tabela alunos
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='alunos'")
        alunos_table = cursor.fetchone()
        assert alunos_table is not None, "Tabela alunos deve ser criada"
        
        conn.close()
    
    def test_init_db_creates_default_admin_user(self):
        """
        Testa se init_db cria o usuário admin padrão
        """
        # Act
        db.init_db()
        
        # Assert - Verificar se usuário admin foi criado
        conn = db.get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT username, password FROM users WHERE username='admin'")
        admin_user = cursor.fetchone()
        
        assert admin_user is not None, "Usuário admin deve ser criado"
        assert admin_user[0] == 'admin', "Username deve ser 'admin'"
        assert admin_user[1] == 'senha', "Password padrão deve ser 'senha'"
        conn.close()
    
    def test_validar_login_function_exists(self):
        """
        Testa se função validar_login existe e é chamável
        """
        # Assert
        assert hasattr(db, 'validar_login'), "Função validar_login deve existir"
        assert callable(db.validar_login), "validar_login deve ser chamável"
    
    def test_validar_login_basic_behavior(self):
        """
        Testa comportamento básico da função validar_login
        """
        # Arrange
        db.init_db()
        
        # Act - Testar diferentes tipos de resultado
        resultado_admin = db.validar_login('admin', 'senha')
        resultado_invalido = db.validar_login('invalido', 'invalido')
        
        # Assert - Verificar que função retorna algo (pode ser tupla, bool, etc.)
        assert resultado_admin is not None, "Deve retornar algo para credenciais corretas"
        
        # Para credenciais incorretas, pode retornar None ou False
        assert resultado_invalido is None or resultado_invalido is False, "Deve indicar falha para credenciais incorretas"
        
        # Se for tupla, verificar estrutura
        if isinstance(resultado_admin, tuple):
            assert len(resultado_admin) >= 1, "Tupla deve ter pelo menos 1 elemento"
    
    def test_get_conn_returns_valid_connection(self):
        """
        Testa se get_conn retorna uma conexão válida
        """
        # Arrange
        db.init_db()  # Garante que o DB existe
        
        # Act
        conn = db.get_conn()
        
        # Assert
        assert conn is not None, "Deve retornar uma conexão"
        assert isinstance(conn, sqlite3.Connection), "Deve ser uma conexão SQLite"
        
        # Verificar se a conexão funciona
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        assert result[0] == 1, "Conexão deve estar funcional"
        
        conn.close()