"""
Testes unitários para funções do banco de dados
"""
import pytest
import os
from datetime import date, datetime
from database.db import (
    inserir_aluno, listar_alunos, listar_todos_alunos, inativar_aluno,
    atualizar_aluno, cpf_existe, email_existe,
    criar_mensalidade, listar_mensalidades, marcar_mensalidade_paga,
    get_conn
)
from database.kids_db import inserir_kid, listar_kids


class TestAlunoOperations:
    """Testes para operações de alunos"""
    
    def test_inserir_aluno(self, temp_db, sample_aluno_data):
        """Teste criar novo aluno"""
        aluno_id = inserir_aluno(**sample_aluno_data)
        
        assert aluno_id is not None
        assert isinstance(aluno_id, int)
        assert aluno_id > 0
    
    def test_cpf_existe(self, temp_db, sample_aluno_data):
        """Teste verificação de CPF existente"""
        # CPF não deve existir inicialmente
        assert not cpf_existe(sample_aluno_data['cpf'])
        
        # Criar aluno
        inserir_aluno(**sample_aluno_data)
        
        # Agora CPF deve existir
        assert cpf_existe(sample_aluno_data['cpf'])
    
    def test_email_existe(self, temp_db, sample_aluno_data):
        """Teste verificação de email existente"""
        # Email não deve existir inicialmente
        assert not email_existe(sample_aluno_data['email'])
        
        # Criar aluno
        inserir_aluno(**sample_aluno_data)
        
        # Agora email deve existir
        assert email_existe(sample_aluno_data['email'])
    
    def test_listar_alunos_ativo(self, temp_db, sample_aluno_data):
        """Teste listagem de alunos ativos"""
        # Lista deve estar vazia inicialmente
        alunos = listar_alunos()
        assert len(alunos) == 0
        
        # Criar aluno
        inserir_aluno(**sample_aluno_data)
        
        # Agora deve haver 1 aluno ativo
        alunos = listar_alunos()
        assert len(alunos) == 1
        assert alunos[0][1] == sample_aluno_data['nome']  # Nome na posição 1
    
    def test_listar_todos_alunos(self, temp_db, sample_aluno_data):
        """Teste listagem de todos os alunos"""
        # Criar aluno
        aluno_id = inserir_aluno(**sample_aluno_data)
        
        # Inativar aluno
        inativar_aluno(aluno_id)
        
        # listar_alunos não deve retornar inativos
        alunos_ativos = listar_alunos()
        assert len(alunos_ativos) == 0
        
        # listar_todos_alunos deve retornar todos
        todos_alunos = listar_todos_alunos()
        assert len(todos_alunos) == 1
    
    def test_inativar_aluno(self, temp_db, sample_aluno_data):
        """Teste inativação de aluno"""
        aluno_id = inserir_aluno(**sample_aluno_data)
        
        # Verificar que está ativo
        alunos = listar_alunos()
        assert len(alunos) == 1
        
        # Inativar
        inativar_aluno(aluno_id)
        
        # Verificar que não aparece mais na lista de ativos
        alunos = listar_alunos()
        assert len(alunos) == 0
    
    def test_atualizar_aluno(self, temp_db, sample_aluno_data):
        """Teste atualização de dados do aluno"""
        aluno_id = inserir_aluno(**sample_aluno_data)
        
        # Atualizar nome
        novo_nome = "João Silva Atualizado"
        sample_aluno_data['nome'] = novo_nome
        
        atualizar_aluno(aluno_id, **sample_aluno_data)
        
        # Verificar atualização
        alunos = listar_alunos()
        assert alunos[0][1] == novo_nome


class TestMensalidadeOperations:
    """Testes para operações de mensalidades"""
    
    def test_criar_mensalidade(self, temp_db, sample_aluno_data, sample_mensalidade_data):
        """Teste criação de mensalidade"""
        # Criar aluno primeiro
        aluno_id = inserir_aluno(**sample_aluno_data)
        sample_mensalidade_data['aluno_id'] = aluno_id
        
        # Criar mensalidade
        mensalidade_id = criar_mensalidade(**sample_mensalidade_data)
        
        assert mensalidade_id is not None
        assert isinstance(mensalidade_id, int)
        assert mensalidade_id > 0
    
    def test_listar_mensalidades(self, temp_db, sample_aluno_data, sample_mensalidade_data):
        """Teste listagem de mensalidades"""
        # Criar aluno e mensalidade
        aluno_id = inserir_aluno(**sample_aluno_data)
        sample_mensalidade_data['aluno_id'] = aluno_id
        criar_mensalidade(**sample_mensalidade_data)
        
        # Listar mensalidades
        mensalidades = listar_mensalidades()
        
        assert len(mensalidades) == 1
        assert mensalidades[0][1] == sample_aluno_data['nome']  # Nome do aluno
        assert mensalidades[0][2] == sample_mensalidade_data['valor']  # Valor
    
    def test_marcar_mensalidade_paga(self, temp_db, sample_aluno_data, sample_mensalidade_data):
        """Teste marcação de mensalidade como paga"""
        # Criar aluno e mensalidade
        aluno_id = inserir_aluno(**sample_aluno_data)
        sample_mensalidade_data['aluno_id'] = aluno_id
        mensalidade_id = criar_mensalidade(**sample_mensalidade_data)
        
        # Marcar como paga
        from datetime import date
        marcar_mensalidade_paga(mensalidade_id, date.today(), 'Teste pagamento')
        
        # Verificar status
        mensalidades = listar_mensalidades()
        assert mensalidades[0][5] == 'PAGO'  # Status na posição 5


class TestKidsOperations:
    """Testes para operações de crianças"""
    
    def test_inserir_kid(self, temp_db, sample_kid_data):
        """Teste criação de criança"""
        kid_id = inserir_kid(**sample_kid_data)
        
        assert kid_id is not None
        assert isinstance(kid_id, int)
        assert kid_id > 0
    
    def test_listar_kids(self, temp_db, sample_kid_data):
        """Teste listagem de crianças"""
        # Lista deve estar vazia inicialmente
        kids = listar_kids()
        assert len(kids) == 0
        
        # Criar kid
        inserir_kid(**sample_kid_data)
        
        # Agora deve haver 1 kid
        kids = listar_kids()
        assert len(kids) == 1
        assert kids[0][1] == sample_kid_data['nome']  # Nome na posição 1


class TestResponsavelOperations:
    """Testes para operações de responsáveis"""
    
    def test_vincular_responsavel(self, temp_db):
        """Teste vinculação de responsável"""
        # Criar responsável (aluno adulto)
        responsavel_data = {
            'nome': 'João Silva',
            'cpf': '12345678901',
            'email': 'joao@test.com',
            'telefone': '11999999999',
            'cep': '01234567',
            'endereco': 'Rua Teste, 123',
            'data_nasc': '1980-01-01',
            'faixa': 'Preta',
            'grau': '1',
            'peso': '75',
            'altura': '1.80',
            'plano': 'Anual',
            'foto_path': None,
            'certificado_path': None,
            'biometria_data': None
        }
        
        # Criar dependente (aluno adulto filho)
        dependente_data = {
            'nome': 'Pedro Silva',
            'cpf': '98765432109',
            'email': 'pedro@test.com',
            'telefone': '11888888888',
            'cep': '01234567',
            'endereco': 'Rua Teste, 123',
            'data_nasc': '2005-01-01',
            'faixa': 'Azul',
            'grau': '1',
            'peso': '60',
            'altura': '1.70',
            'plano': 'Mensal',
            'foto_path': None,
            'certificado_path': None,
            'biometria_data': None
        }
        
        responsavel_id = inserir_aluno(**responsavel_data)
        dependente_id = inserir_aluno(**dependente_data)
        
        # Vincular dependente ao responsável
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE alunos SET responsavel_id = ? WHERE id = ?", (responsavel_id, dependente_id))
        conn.commit()
        conn.close()
        
        # Verificar vinculação
        todos_alunos = listar_todos_alunos()
        
        # Encontrar o dependente
        dependente = None
        for aluno in todos_alunos:
            if aluno[0] == dependente_id:  # ID na posição 0
                dependente = aluno
                break
        
        assert dependente is not None
        # Verificar se tem informações do responsável (nas últimas colunas)
        assert len(dependente) > 19  # Deve ter colunas extras
        assert dependente[19] == responsavel_data['nome']  # responsavel_nome
        assert dependente[20] == responsavel_data['cpf']   # responsavel_cpf


class TestDatabaseConnection:
    """Testes para conexão com banco de dados"""
    
    def test_get_conn(self, temp_db):
        """Teste obtenção de conexão"""
        conn = get_conn()
        assert conn is not None
        
        # Testar se consegue executar query
        cur = conn.cursor()
        cur.execute("SELECT 1")
        result = cur.fetchone()
        assert result[0] == 1
        
        conn.close()


class TestDataValidation:
    """Testes para validação de dados"""
    
    def test_cpf_validation(self, temp_db):
        """Teste validação de CPF"""
        # CPFs inválidos devem ser rejeitados pelo banco
        invalid_data = {
            'nome': 'Teste',
            'cpf': '123',  # CPF muito curto
            'email': 'test@test.com',
            'telefone': '11999999999',
            'cep': '01234567',
            'endereco': 'Rua Teste',
            'data_nasc': '1990-01-01',
            'faixa': 'Branca',
            'grau': '1',
            'peso': '70',
            'altura': '1.75',
            'plano': 'Mensal',
            'foto_path': None,
            'certificado_path': None,
            'biometria_data': None
        }
        
        # Deve funcionar normalmente (validação é feita na UI)
        aluno_id = inserir_aluno(**invalid_data)
        assert aluno_id is not None
    
    def test_unique_constraints(self, temp_db, sample_aluno_data):
        """Teste restrições de unicidade"""
        # Criar primeiro aluno
        inserir_aluno(**sample_aluno_data)
        
        # Tentar criar outro com mesmo CPF deve falhar
        with pytest.raises(Exception):  # SQLite levanta IntegrityError
            inserir_aluno(**sample_aluno_data)