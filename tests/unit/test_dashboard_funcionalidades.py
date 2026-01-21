"""
Testes para funcionalidades do Dashboard
- Métricas dashboard
- Geração de mensalidades anuais
- Integração com dados existentes
"""

import pytest
from datetime import date, timedelta
from database.db import (
    obter_metricas_dashboard, 
    gerar_mensalidades_anuais,
    inserir_aluno,
    criar_mensalidade,
    marcar_mensalidade_paga,
    get_conn
)


class TestDashboardMetricas:
    """Testa as métricas do dashboard"""
    
    def test_metricas_dashboard_estrutura_basica(self, temp_db):
        """Testa se a função retorna a estrutura correta"""
        metricas = obter_metricas_dashboard()
        
        # Verificar estrutura de retorno
        assert 'atrasadas' in metricas
        assert 'pagas_mes' in metricas
        assert 'a_vencer' in metricas
        assert 'receita_anual' in metricas
        assert 'alunos' in metricas
        
        # Verificar estrutura das métricas financeiras
        assert 'count' in metricas['atrasadas']
        assert 'valor' in metricas['atrasadas']
        assert 'count' in metricas['pagas_mes']
        assert 'valor' in metricas['pagas_mes']
        assert 'count' in metricas['a_vencer']
        assert 'valor' in metricas['a_vencer']
        
        # Verificar estrutura dos alunos
        assert 'responsaveis' in metricas['alunos']
        assert 'dependentes' in metricas['alunos']
        assert 'kids' in metricas['alunos']
        assert 'bolsistas' in metricas['alunos']
        assert 'total' in metricas['alunos']

    def test_metricas_sem_dados(self, temp_db):
        """Testa métricas quando não há dados"""
        metricas = obter_metricas_dashboard()
        
        # Todos os contadores devem ser zero
        assert metricas['atrasadas']['count'] == 0
        assert metricas['atrasadas']['valor'] == 0
        assert metricas['pagas_mes']['count'] == 0
        assert metricas['pagas_mes']['valor'] == 0
        assert metricas['a_vencer']['count'] == 0
        assert metricas['a_vencer']['valor'] == 0
        assert metricas['receita_anual'] == 0
        assert metricas['alunos']['responsaveis'] == 0
        assert metricas['alunos']['dependentes'] == 0
        assert metricas['alunos']['kids'] == 0
        assert metricas['alunos']['bolsistas'] == 0
        assert metricas['alunos']['total'] == 0

    def test_metricas_mensalidades_atrasadas(self, temp_db):
        """Testa contagem de mensalidades atrasadas"""
        # Criar aluno
        aluno_id = inserir_aluno(**{
            'nome': 'João Atrasado',
            'cpf': '12345678901',
            'email': 'joao@test.com',
            'telefone': '11999999999',
            'cep': '01234567',
            'endereco': 'Rua Teste, 123',
            'data_nasc': '1990-01-01',
            'faixa': 'Branca',
            'grau': '1',
            'peso': '80',
            'altura': '1.80',
            'plano': 'Mensal - R$200',
            'foto_path': None,
            'certificado_path': None,
            'biometria_data': None
        })
        
        # Criar mensalidade atrasada (data passada)
        data_atrasada = date.today() - timedelta(days=30)
        criar_mensalidade(aluno_id, 200.0, data_atrasada, 'Mensalidade atrasada')
        
        # Verificar métricas
        metricas = obter_metricas_dashboard()
        assert metricas['atrasadas']['count'] == 1
        assert metricas['atrasadas']['valor'] == 200.0

    def test_metricas_mensalidades_a_vencer(self, temp_db):
        """Testa contagem de mensalidades a vencer"""
        # Criar aluno
        aluno_id = inserir_aluno(**{
            'nome': 'Maria A Vencer',
            'cpf': '12345678902',
            'email': 'maria@test.com',
            'telefone': '11999999999',
            'cep': '01234567',
            'endereco': 'Rua Teste, 123',
            'data_nasc': '1985-05-15',
            'faixa': 'Azul',
            'grau': '2',
            'peso': '60',
            'altura': '1.65',
            'plano': 'Mensal - R$180',
            'foto_path': None,
            'certificado_path': None,
            'biometria_data': None
        })
        
        # Criar mensalidade a vencer (próximos 15 dias)
        data_a_vencer = date.today() + timedelta(days=15)
        criar_mensalidade(aluno_id, 180.0, data_a_vencer, 'Mensalidade a vencer')
        
        # Verificar métricas
        metricas = obter_metricas_dashboard()
        assert metricas['a_vencer']['count'] == 1
        assert metricas['a_vencer']['valor'] == 180.0

    def test_metricas_mensalidades_pagas_no_mes(self, temp_db):
        """Testa contagem de mensalidades pagas no mês atual"""
        # Criar aluno
        aluno_id = inserir_aluno(**{
            'nome': 'Carlos Pagou',
            'cpf': '12345678903',
            'email': 'carlos@test.com',
            'telefone': '11999999999',
            'cep': '01234567',
            'endereco': 'Rua Teste, 123',
            'data_nasc': '1988-03-20',
            'faixa': 'Roxa',
            'grau': '1',
            'peso': '75',
            'altura': '1.75',
            'plano': 'Mensal - R$220',
            'foto_path': None,
            'certificado_path': None,
            'biometria_data': None
        })
        
        # Criar mensalidade e marcar como paga no mês atual
        mensalidade_id = criar_mensalidade(aluno_id, 220.0, date.today(), 'Mensalidade paga')
        marcar_mensalidade_paga(mensalidade_id, date.today(), 'Pagamento teste')
        
        # Verificar métricas
        metricas = obter_metricas_dashboard()
        assert metricas['pagas_mes']['count'] == 1
        assert metricas['pagas_mes']['valor'] == 220.0

    def test_metricas_exclui_dependentes(self, temp_db):
        """Testa que dependentes são excluídos das métricas"""
        # Criar responsável
        responsavel_id = inserir_aluno(**{
            'nome': 'Responsável Pai',
            'cpf': '11111111111',
            'email': 'pai@test.com',
            'telefone': '11999999999',
            'cep': '01234567',
            'endereco': 'Rua Teste, 123',
            'data_nasc': '1980-01-01',
            'faixa': 'Preta',
            'grau': '1',
            'peso': '80',
            'altura': '1.80',
            'plano': 'Família - R$300',
            'foto_path': None,
            'certificado_path': None,
            'biometria_data': None
        })
        
        # Criar dependente
        dependente_id = inserir_aluno(**{
            'nome': 'Dependente Filho',
            'cpf': '22222222222',
            'email': 'filho@test.com',
            'telefone': '11999999999',
            'cep': '01234567',
            'endereco': 'Rua Teste, 123',
            'data_nasc': '2010-01-01',
            'faixa': 'Branca',
            'grau': '1',
            'peso': '40',
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
        
        # Criar mensalidades para ambos
        criar_mensalidade(responsavel_id, 300.0, date.today() - timedelta(days=5), 'Mensalidade responsável')
        criar_mensalidade(dependente_id, 150.0, date.today() - timedelta(days=5), 'Mensalidade dependente')
        
        # Verificar métricas - apenas responsável deve aparecer
        metricas = obter_metricas_dashboard()
        assert metricas['atrasadas']['count'] == 1
        assert metricas['atrasadas']['valor'] == 300.0


class TestGeracaoMensalidadesAnuais:
    """Testa a geração de mensalidades anuais"""
    
    def test_geracao_anuais_estrutura_retorno(self, temp_db):
        """Testa se a função retorna um número"""
        resultado = gerar_mensalidades_anuais()
        
        # Deve retornar um inteiro
        assert isinstance(resultado, int)
        assert resultado >= 0

    def test_geracao_anuais_sem_alunos(self, temp_db):
        """Testa geração quando não há alunos"""
        resultado = gerar_mensalidades_anuais()
        
        # Deve retornar 0 mensalidades criadas
        assert resultado == 0

    def test_geracao_anuais_com_alunos(self, temp_db):
        """Testa geração com alunos válidos"""
        # Criar aluno com plano pago
        aluno_id = inserir_aluno(**{
            'nome': 'Ana Anual',
            'cpf': '33333333333',
            'email': 'ana@test.com',
            'telefone': '11999999999',
            'cep': '01234567',
            'endereco': 'Rua Teste, 123',
            'data_nasc': '1992-07-10',
            'faixa': 'Azul',
            'grau': '3',
            'peso': '55',
            'altura': '1.60',
            'plano': 'Mensal - R$190',
            'foto_path': None,
            'certificado_path': None,
            'biometria_data': None
        })
        
        # Gerar mensalidades anuais
        resultado = gerar_mensalidades_anuais()
        
        # Deve ter criado mensalidades
        assert resultado > 0
        
        # Verificar se mensalidades foram criadas no banco
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM mensalidades WHERE aluno_id = ?", (aluno_id,))
        count = cur.fetchone()[0]
        conn.close()
        
        # Deve ter criado pelo menos algumas mensalidades
        assert count > 0

    def test_geracao_anuais_exclui_dependentes(self, temp_db):
        """Testa que dependentes não recebem mensalidades anuais"""
        # Criar responsável
        responsavel_id = inserir_aluno(**{
            'nome': 'Responsável Mãe',
            'cpf': '44444444444',
            'email': 'mae@test.com',
            'telefone': '11999999999',
            'cep': '01234567',
            'endereco': 'Rua Teste, 123',
            'data_nasc': '1985-03-15',
            'faixa': 'Marrom',
            'grau': '1',
            'peso': '65',
            'altura': '1.65',
            'plano': 'Família - R$350',
            'foto_path': None,
            'certificado_path': None,
            'biometria_data': None
        })
        
        # Criar dependente
        dependente_id = inserir_aluno(**{
            'nome': 'Dependente Filha',
            'cpf': '55555555555',
            'email': 'filha@test.com',
            'telefone': '11999999999',
            'cep': '01234567',
            'endereco': 'Rua Teste, 123',
            'data_nasc': '2012-06-20',
            'faixa': 'Branca',
            'grau': '2',
            'peso': '35',
            'altura': '1.30',
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
        
        # Gerar mensalidades anuais
        resultado = gerar_mensalidades_anuais()
        
        # Verificar que apenas o responsável recebeu mensalidades
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM mensalidades WHERE aluno_id = ?", (responsavel_id,))
        mensalidades_responsavel = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM mensalidades WHERE aluno_id = ?", (dependente_id,))
        mensalidades_dependente = cur.fetchone()[0]
        conn.close()
        
        assert mensalidades_responsavel > 0, "Responsável deve ter mensalidades"
        assert mensalidades_dependente == 0, "Dependente não deve ter mensalidades"

    def test_geracao_anuais_exclui_bolsistas(self, temp_db):
        """Testa que bolsistas não recebem mensalidades anuais"""
        # Criar bolsista
        bolsista_id = inserir_aluno(**{
            'nome': 'João Bolsista',
            'cpf': '66666666666',
            'email': 'bolsista@test.com',
            'telefone': '11999999999',
            'cep': '01234567',
            'endereco': 'Rua Teste, 123',
            'data_nasc': '1995-11-30',
            'faixa': 'Azul',
            'grau': '1',
            'peso': '70',
            'altura': '1.70',
            'plano': 'Bolsista Integral - R$0',
            'foto_path': None,
            'certificado_path': None,
            'biometria_data': None
        })
        
        # Gerar mensalidades anuais
        gerar_mensalidades_anuais()
        
        # Verificar que bolsista não recebeu mensalidades
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM mensalidades WHERE aluno_id = ?", (bolsista_id,))
        count = cur.fetchone()[0]
        conn.close()
        
        assert count == 0, "Bolsista não deve receber mensalidades"

    def test_geracao_anuais_ano_especifico(self, temp_db):
        """Testa geração para ano específico"""
        # Criar aluno
        aluno_id = inserir_aluno(**{
            'nome': 'Pedro Futuro',
            'cpf': '77777777777',
            'email': 'pedro@test.com',
            'telefone': '11999999999',
            'cep': '01234567',
            'endereco': 'Rua Teste, 123',
            'data_nasc': '1987-12-25',
            'faixa': 'Roxa',
            'grau': '2',
            'peso': '85',
            'altura': '1.85',
            'plano': 'Mensal - R$210',
            'foto_path': None,
            'certificado_path': None,
            'biometria_data': None
        })
        
        # Gerar mensalidades para 2027
        resultado = gerar_mensalidades_anuais(2027)
        
        # Verificar que mensalidades foram criadas para 2027
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT COUNT(*) FROM mensalidades 
            WHERE aluno_id = ? AND strftime('%Y', data_vencimento) = '2027'
        """, (aluno_id,))
        count_2027 = cur.fetchone()[0]
        conn.close()
        
        assert count_2027 > 0, "Deve ter criado mensalidades para 2027"
        assert resultado > 0