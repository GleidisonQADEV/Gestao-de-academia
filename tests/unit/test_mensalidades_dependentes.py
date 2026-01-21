import pytest
import tempfile
import os
import sys
from datetime import date

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from database.db import (
    init_db, get_conn, inserir_aluno, criar_mensalidade,
    listar_mensalidades, gerar_mensalidades_automaticas
)


class TestMensalidadesDependentes:
    """Testes para verificar que dependentes não aparecem na aba financeiro"""
    
    @pytest.fixture
    def temp_db(self):
        """Criar banco temporário para testes"""
        db_fd, db_path = tempfile.mkstemp()
        
        # Substituir o caminho do banco temporariamente
        import database.db as db_module
        original_db_path = db_module.DB_PATH
        db_module.DB_PATH = db_path
        
        # Inicializar banco
        init_db()
        
        yield db_path
        
        # Limpeza
        db_module.DB_PATH = original_db_path
        os.close(db_fd)
        os.unlink(db_path)
    
    def test_dependentes_nao_aparecem_listagem_mensalidades(self, temp_db):
        """Testa que dependentes vinculados não aparecem na listagem de mensalidades"""
        # Criar responsável
        responsavel_id = inserir_aluno(**{
            'nome': 'Ana Silva',
            'cpf': '11111111111',
            'email': 'ana@test.com',
            'telefone': '11999999999',
            'cep': '01234567',
            'endereco': 'Rua Teste, 123',
            'data_nasc': '1985-05-15',
            'faixa': 'Azul',
            'grau': '2',
            'peso': '65',
            'altura': '1.65',
            'plano': 'Família: 1 adulto + 1 dependente - R$300',
            'foto_path': None,
            'certificado_path': None,
            'biometria_data': None
        })
        
        # Criar dependente
        dependente_id = inserir_aluno(**{
            'nome': 'João Silva',
            'cpf': '22222222222',
            'email': 'joao@test.com',
            'telefone': '11888888888',
            'cep': '01234567',
            'endereco': 'Rua Teste, 123',
            'data_nasc': '2010-08-20',
            'faixa': 'Verde',
            'grau': '1',
            'peso': '45',
            'altura': '1.50',
            'plano': 'Vinculado ao responsável',
            'foto_path': None,
            'certificado_path': None,
            'biometria_data': None
        })
        
        # Vincular dependente ao responsável
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE alunos SET responsavel_id = ? WHERE id = ?", (responsavel_id, dependente_id))
        conn.commit()
        conn.close()
        
        # Criar mensalidades para ambos
        msg_responsavel = criar_mensalidade(responsavel_id, 300.0, date.today(), 'Plano Familiar')
        msg_dependente = criar_mensalidade(dependente_id, 150.0, date.today(), 'Plano Dependente (ÓRFÃ)')
        
        # Verificar listagem - apenas responsável deve aparecer
        mensalidades = listar_mensalidades()
        
        assert len(mensalidades) == 1, "Apenas responsável deve aparecer na listagem"
        assert mensalidades[0][1] == 'Ana Silva', "Responsável deve aparecer"
        assert mensalidades[0][2] == 300.0, "Valor do responsável deve estar correto"
        
        # Verificar que dependente não aparece
        nomes_na_listagem = [m[1] for m in mensalidades]
        assert 'João Silva' not in nomes_na_listagem, "Dependente não deve aparecer na listagem"
    
    def test_geracao_automatica_exclui_dependentes(self, temp_db):
        """Testa que geração automática de mensalidades exclui dependentes"""
        # Criar responsável
        responsavel_id = inserir_aluno(**{
            'nome': 'Maria Santos',
            'cpf': '33333333333',
            'email': 'maria@test.com',
            'telefone': '11777777777',
            'cep': '01234567',
            'endereco': 'Av. Principal, 456',
            'data_nasc': '1980-12-10',
            'faixa': 'Marrom',
            'grau': '1',
            'peso': '70',
            'altura': '1.70',
            'plano': 'Adulto - R$200',
            'foto_path': None,
            'certificado_path': None,
            'biometria_data': None
        })
        
        # Criar dependente
        dependente_id = inserir_aluno(**{
            'nome': 'Pedro Santos',
            'cpf': '44444444444',
            'email': 'pedro@test.com',
            'telefone': '11666666666',
            'cep': '01234567',
            'endereco': 'Av. Principal, 456',
            'data_nasc': '2008-03-25',
            'faixa': 'Amarela',
            'grau': '2',
            'peso': '35',
            'altura': '1.40',
            'plano': 'Vinculado ao responsável',
            'foto_path': None,
            'certificado_path': None,
            'biometria_data': None
        })
        
        # Vincular dependente ao responsável
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE alunos SET responsavel_id = ? WHERE id = ?", (responsavel_id, dependente_id))
        conn.commit()
        conn.close()
        
        # Gerar mensalidades automáticas
        mensalidades_criadas = gerar_mensalidades_automaticas()
        
        # Verificar que apenas 1 mensalidade foi criada (para o responsável)
        assert mensalidades_criadas == 1, "Apenas responsável deve ter mensalidade gerada"
        
        # Verificar listagem
        mensalidades = listar_mensalidades()
        assert len(mensalidades) == 1, "Apenas responsável deve aparecer"
        assert mensalidades[0][1] == 'Maria Santos', "Responsável deve ter mensalidade"
        
        # Verificar que não há mensalidades para o dependente
        nomes_na_listagem = [m[1] for m in mensalidades]
        assert 'Pedro Santos' not in nomes_na_listagem, "Dependente não deve ter mensalidade gerada"
    
    def test_multiplos_dependentes_um_responsavel(self, temp_db):
        """Testa cenário com múltiplos dependentes vinculados a um responsável"""
        # Criar responsável
        responsavel_id = inserir_aluno(**{
            'nome': 'Carlos Oliveira',
            'cpf': '55555555555',
            'email': 'carlos@test.com',
            'telefone': '11555555555',
            'cep': '01234567',
            'endereco': 'Rua Família, 789',
            'data_nasc': '1975-07-30',
            'faixa': 'Preta',
            'grau': '1',
            'peso': '80',
            'altura': '1.80',
            'plano': 'Família: 1 adulto + 2 dependentes - R$400',
            'foto_path': None,
            'certificado_path': None,
            'biometria_data': None
        })
        
        # Criar primeiro dependente
        dependente1_id = inserir_aluno(**{
            'nome': 'Laura Oliveira',
            'cpf': '66666666666',
            'email': 'laura@test.com',
            'telefone': '11444444444',
            'cep': '01234567',
            'endereco': 'Rua Família, 789',
            'data_nasc': '2005-11-15',
            'faixa': 'Azul',
            'grau': '1',
            'peso': '50',
            'altura': '1.60',
            'plano': 'Vinculado ao responsável',
            'foto_path': None,
            'certificado_path': None,
            'biometria_data': None
        })
        
        # Criar segundo dependente
        dependente2_id = inserir_aluno(**{
            'nome': 'Bruno Oliveira',
            'cpf': '77777777777',
            'email': 'bruno@test.com',
            'telefone': '11333333333',
            'cep': '01234567',
            'endereco': 'Rua Família, 789',
            'data_nasc': '2012-01-08',
            'faixa': 'Verde',
            'grau': '1',
            'peso': '30',
            'altura': '1.30',
            'plano': 'Vinculado ao responsável',
            'foto_path': None,
            'certificado_path': None,
            'biometria_data': None
        })
        
        # Vincular ambos dependentes ao responsável
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE alunos SET responsavel_id = ? WHERE id = ?", (responsavel_id, dependente1_id))
        cur.execute("UPDATE alunos SET responsavel_id = ? WHERE id = ?", (responsavel_id, dependente2_id))
        conn.commit()
        conn.close()
        
        # Criar mensalidades para todos (simulando situação anterior às correções)
        criar_mensalidade(responsavel_id, 400.0, date.today(), 'Plano Familiar')
        criar_mensalidade(dependente1_id, 120.0, date.today(), 'Dependente 1 (ÓRFÃ)')
        criar_mensalidade(dependente2_id, 100.0, date.today(), 'Dependente 2 (ÓRFÃ)')
        
        # Verificar listagem - apenas responsável deve aparecer
        mensalidades = listar_mensalidades()
        
        assert len(mensalidades) == 1, "Apenas responsável deve aparecer na listagem"
        assert mensalidades[0][1] == 'Carlos Oliveira', "Responsável deve aparecer"
        assert mensalidades[0][2] == 400.0, "Valor do responsável deve estar correto"
        
        # Verificar que dependentes não aparecem
        nomes_na_listagem = [m[1] for m in mensalidades]
        assert 'Laura Oliveira' not in nomes_na_listagem, "Dependente 1 não deve aparecer"
        assert 'Bruno Oliveira' not in nomes_na_listagem, "Dependente 2 não deve aparecer"
    
    def test_filtro_status_com_dependentes(self, temp_db):
        """Testa filtro por status excluindo dependentes"""
        # Criar responsável
        responsavel_id = inserir_aluno(**{
            'nome': 'Rita Costa',
            'cpf': '88888888888',
            'email': 'rita@test.com',
            'telefone': '11222222222',
            'cep': '01234567',
            'endereco': 'Av. Teste, 999',
            'data_nasc': '1988-09-12',
            'faixa': 'Roxa',
            'grau': '1',
            'peso': '58',
            'altura': '1.62',
            'plano': 'Adulto - R$180',
            'foto_path': None,
            'certificado_path': None,
            'biometria_data': None
        })
        
        # Criar dependente
        dependente_id = inserir_aluno(**{
            'nome': 'Lucas Costa',
            'cpf': '99999999999',
            'email': 'lucas@test.com',
            'telefone': '11111111111',
            'cep': '01234567',
            'endereco': 'Av. Teste, 999',
            'data_nasc': '2015-06-18',
            'faixa': 'Branca',
            'grau': '1',
            'peso': '25',
            'altura': '1.20',
            'plano': 'Vinculado ao responsável',
            'foto_path': None,
            'certificado_path': None,
            'biometria_data': None
        })
        
        # Vincular dependente
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE alunos SET responsavel_id = ? WHERE id = ?", (responsavel_id, dependente_id))
        conn.commit()
        conn.close()
        
        # Criar mensalidades com status diferentes
        criar_mensalidade(responsavel_id, 180.0, date.today(), 'Responsável PENDENTE')
        criar_mensalidade(dependente_id, 90.0, date.today(), 'Dependente PENDENTE (ÓRFÃ)')
        
        # Marcar mensalidade do dependente como paga (simulação)
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE mensalidades SET status = 'PAGO' WHERE aluno_id = ?", (dependente_id,))
        conn.commit()
        conn.close()
        
        # Testar filtro PENDENTE - apenas responsável deve aparecer
        mensalidades_pendentes = listar_mensalidades('PENDENTE')
        assert len(mensalidades_pendentes) == 1, "Apenas responsável pendente deve aparecer"
        assert mensalidades_pendentes[0][1] == 'Rita Costa', "Responsável deve aparecer"
        
        # Testar filtro PAGO - nenhuma deve aparecer (dependente não conta)
        mensalidades_pagas = listar_mensalidades('PAGO')
        assert len(mensalidades_pagas) == 0, "Dependente pago não deve aparecer na listagem"
        
        # Testar listagem geral - apenas responsável
        todas_mensalidades = listar_mensalidades()
        assert len(todas_mensalidades) == 1, "Apenas responsável deve aparecer no total"
    
    def test_aluno_sem_vinculo_aparece_normal(self, temp_db):
        """Testa que alunos sem vínculo (não dependentes) aparecem normalmente"""
        # Criar aluno independente
        aluno_id = inserir_aluno(**{
            'nome': 'Independente Silva',
            'cpf': '10101010101',
            'email': 'independente@test.com',
            'telefone': '11000000000',
            'cep': '01234567',
            'endereco': 'Rua Independência, 123',
            'data_nasc': '1990-04-22',
            'faixa': 'Azul',
            'grau': '3',
            'peso': '75',
            'altura': '1.75',
            'plano': 'Adulto - R$200',
            'foto_path': None,
            'certificado_path': None,
            'biometria_data': None
        })
        
        # Criar mensalidade
        criar_mensalidade(aluno_id, 200.0, date.today(), 'Aluno independente')
        
        # Verificar que aparece na listagem
        mensalidades = listar_mensalidades()
        assert len(mensalidades) == 1, "Aluno independente deve aparecer"
        assert mensalidades[0][1] == 'Independente Silva', "Nome deve estar correto"
        assert mensalidades[0][2] == 200.0, "Valor deve estar correto"
    
    def test_cenario_misto_responsaveis_e_independentes(self, temp_db):
        """Testa cenário com responsáveis, dependentes e alunos independentes"""
        # Criar responsável
        responsavel_id = inserir_aluno(**{
            'nome': 'Responsável Família',
            'cpf': '12121212121',
            'email': 'responsavel@test.com',
            'telefone': '11111111111',
            'cep': '01234567',
            'endereco': 'Rua Família, 100',
            'data_nasc': '1982-01-01',
            'faixa': 'Preta',
            'grau': '2',
            'peso': '75',
            'altura': '1.75',
            'plano': 'Família - R$350',
            'foto_path': None,
            'certificado_path': None,
            'biometria_data': None
        })
        
        # Criar dependente
        dependente_id = inserir_aluno(**{
            'nome': 'Dependente Família',
            'cpf': '21212121212',
            'email': 'dependente@test.com',
            'telefone': '11222222222',
            'cep': '01234567',
            'endereco': 'Rua Família, 100',
            'data_nasc': '2010-01-01',
            'faixa': 'Verde',
            'grau': '1',
            'peso': '40',
            'altura': '1.40',
            'plano': 'Vinculado ao responsável',
            'foto_path': None,
            'certificado_path': None,
            'biometria_data': None
        })
        
        # Criar aluno independente
        independente_id = inserir_aluno(**{
            'nome': 'Aluno Independente',
            'cpf': '13131313131',
            'email': 'independente@test.com',
            'telefone': '11333333333',
            'cep': '01234567',
            'endereco': 'Rua Solo, 200',
            'data_nasc': '1995-06-15',
            'faixa': 'Azul',
            'grau': '1',
            'peso': '70',
            'altura': '1.70',
            'plano': 'Adulto - R$180',
            'foto_path': None,
            'certificado_path': None,
            'biometria_data': None
        })
        
        # Vincular dependente
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE alunos SET responsavel_id = ? WHERE id = ?", (responsavel_id, dependente_id))
        conn.commit()
        conn.close()
        
        # Criar mensalidades para todos
        criar_mensalidade(responsavel_id, 350.0, date.today(), 'Família')
        criar_mensalidade(dependente_id, 120.0, date.today(), 'Dependente (ÓRFÃ)')
        criar_mensalidade(independente_id, 180.0, date.today(), 'Independente')
        
        # Verificar listagem - apenas responsável e independente devem aparecer
        mensalidades = listar_mensalidades()
        assert len(mensalidades) == 2, "Apenas responsável e independente devem aparecer"
        
        nomes_na_listagem = [m[1] for m in mensalidades]
        assert 'Responsável Família' in nomes_na_listagem, "Responsável deve aparecer"
        assert 'Aluno Independente' in nomes_na_listagem, "Independente deve aparecer"
        assert 'Dependente Família' not in nomes_na_listagem, "Dependente não deve aparecer"
        
        # Verificar valores totais
        valor_total = sum(m[2] for m in mensalidades)
        assert valor_total == 530.0, "Valor total deve ser responsável + independente (350 + 180)"