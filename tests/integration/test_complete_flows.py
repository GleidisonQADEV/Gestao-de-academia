"""
Testes de integração para funcionalidades completas do sistema
"""
import pytest
from datetime import date, datetime
from database.db import (
    inserir_aluno, criar_mensalidade, 
    listar_mensalidades, listar_todos_alunos,
    marcar_mensalidade_paga, get_conn
)
from database.kids_db import inserir_kid


class TestFluxoCompletoAluno:
    """Testes de integração para fluxo completo de gestão de alunos"""
    
    def test_ciclo_completo_aluno_adulto(self, temp_db):
        """Teste ciclo completo: criar → listar → atualizar → inativar aluno adulto"""
        from datetime import date
        
        # 1. Criar aluno
        aluno_data = {
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
        
        aluno_id = inserir_aluno(**aluno_data)
        assert aluno_id is not None
        
        # 2. Criar mensalidade para o aluno
        mensalidade_data = {
            'aluno_id': aluno_id,
            'valor': 150.0,
            'data_vencimento': date.today(),
            'observacoes': 'Primeira mensalidade'
        }
        
        mensalidade_id = criar_mensalidade(**mensalidade_data)
        assert mensalidade_id is not None
        
        # 3. Listar mensalidades e verificar aluno
        mensalidades = listar_mensalidades()
        assert len(mensalidades) == 1
        assert mensalidades[0][1] == aluno_data['nome']
        assert mensalidades[0][2] == 150.0
        assert mensalidades[0][5] == 'PENDENTE'
        
        # 4. Marcar mensalidade como paga
        marcar_mensalidade_paga(mensalidade_id, date.today(), 'Pagamento teste')
        
        # 5. Verificar status atualizado
        mensalidades_atualizadas = listar_mensalidades()
        assert mensalidades_atualizadas[0][5] == 'PAGO'
        assert mensalidades_atualizadas[0][4] is not None  # data_pagamento preenchida
    
    def test_fluxo_responsavel_dependente(self, temp_db):
        """Teste integração completa responsável → dependente"""
        # 1. Criar responsável (aluno adulto)
        responsavel_data = {
            'nome': 'Maria Silva',
            'cpf': '11111111111',
            'email': 'maria@test.com',
            'telefone': '11888888888',
            'cep': '01234567',
            'endereco': 'Rua Família, 456',
            'data_nasc': '1985-03-15',
            'faixa': 'Azul',
            'grau': '2',
            'peso': '65',
            'altura': '1.65',
            'plano': 'Familiar',
            'foto_path': None,
            'certificado_path': None,
            'biometria_data': None
        }
        
        responsavel_id = inserir_aluno(**responsavel_data)
        
        # 2. Criar dependente (kid)
        kid_data = {
            'nome': 'Ana Silva',
            'cpf': '22222222222',
            'resp_nome': 'Maria Silva',
            'resp_cpf': '11111111111',
            'email': 'ana@test.com',
            'telefone': '11777777777',
            'cep': '01234567',
            'endereco': 'Rua Família, 456',
            'data_nasc': '2010-05-20',
            'faixa': 'Amarela',
            'grau': '1',
            'peso': '40',
            'altura': '1.40',
            'plano': 'Kids',
            'foto_path': None,
            'certificado_path': None,
            'biometria_data': None
        }
        
        kid_id = inserir_kid(**kid_data)
        
        # 3. Criar dependente adulto vinculado
        dependente_adulto_data = {
            'nome': 'Pedro Silva',
            'cpf': '33333333333',
            'email': 'pedro@test.com',
            'telefone': '11666666666',
            'cep': '01234567',
            'endereco': 'Rua Família, 456',
            'data_nasc': '2005-08-10',
            'faixa': 'Verde',
            'grau': '1',
            'peso': '55',
            'altura': '1.60',
            'plano': 'Juvenil',
            'foto_path': None,
            'certificado_path': None,
            'biometria_data': None
        }
        
        dependente_id = inserir_aluno(**dependente_adulto_data)
        
        # 4. Vincular dependente adulto ao responsável
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE alunos SET responsavel_id = ? WHERE id = ?", (responsavel_id, dependente_id))
        conn.commit()
        conn.close()
        
        # 5. Verificar vínculos na listagem completa
        todos_alunos = listar_todos_alunos()
        
        # Verificar responsável
        responsavel = None
        dependente = None
        
        for aluno in todos_alunos:
            if aluno[0] == responsavel_id:
                responsavel = aluno
            elif aluno[0] == dependente_id:
                dependente = aluno
        
        assert responsavel is not None
        assert dependente is not None
        
        # 6. Verificar se responsável tem dependentes
        assert len(responsavel) > 21  # Tem colunas extras
        assert responsavel[21] is not None  # dependentes_nomes
        assert responsavel[22] > 0  # total_dependentes
        assert 'Pedro Silva' in responsavel[21]  # Nome do dependente
        
        # 7. Verificar se dependente tem responsável
        assert dependente[19] == 'Maria Silva'  # responsavel_nome
        assert dependente[20] == '11111111111'  # responsavel_cpf
        
        # 8. Criar mensalidades para toda a família
        # Responsável
        criar_mensalidade(responsavel_id, 200.0, date.today(), 'Mensalidade responsável')
        
        # Dependente adulto  
        criar_mensalidade(dependente_id, 100.0, date.today(), 'Mensalidade dependente')
        
        # Kid (ID negativo no sistema de mensalidades)
        criar_mensalidade(-kid_id, 80.0, date.today(), 'Mensalidade kid')
        
        # 9. Verificar mensalidades da família
        mensalidades_familia = listar_mensalidades()
        assert len(mensalidades_familia) == 3
        
        # Verificar valores
        valores = [m[2] for m in mensalidades_familia]
        assert 200.0 in valores  # Responsável
        assert 100.0 in valores  # Dependente
        assert 80.0 in valores   # Kid


class TestFluxoFinanceiro:
    """Testes de integração para fluxos financeiros"""
    
    def test_gestao_mensalidades_multiplos_alunos(self, temp_db):
        """Teste gestão de mensalidades para múltiplos alunos"""
        # Criar 3 alunos
        alunos_data = [
            {
                'nome': 'João Santos',
                'cpf': '11111111111',
                'email': 'joao@test.com',
                'telefone': '11999999999',
                'cep': '01234567',
                'endereco': 'Rua A, 123',
                'data_nasc': '1990-01-01',
                'faixa': 'Branca',
                'grau': '1',
                'peso': '75',
                'altura': '1.80',
                'plano': 'Mensal',
                'foto_path': None,
                'certificado_path': None,
                'biometria_data': None
            },
            {
                'nome': 'Maria Costa',
                'cpf': '22222222222', 
                'email': 'maria@test.com',
                'telefone': '11888888888',
                'cep': '01234567',
                'endereco': 'Rua B, 456',
                'data_nasc': '1985-05-15',
                'faixa': 'Azul',
                'grau': '2',
                'peso': '60',
                'altura': '1.65',
                'plano': 'Trimestral',
                'foto_path': None,
                'certificado_path': None,
                'biometria_data': None
            },
            {
                'nome': 'Carlos Lima',
                'cpf': '33333333333',
                'email': 'carlos@test.com',
                'telefone': '11777777777',
                'cep': '01234567',
                'endereco': 'Rua C, 789',
                'data_nasc': '1992-12-30',
                'faixa': 'Roxa',
                'grau': '1',
                'peso': '80',
                'altura': '1.75',
                'plano': 'Anual',
                'foto_path': None,
                'certificado_path': None,
                'biometria_data': None
            }
        ]
        
        alunos_ids = []
        for aluno_data in alunos_data:
            aluno_id = inserir_aluno(**aluno_data)
            alunos_ids.append(aluno_id)
        
        # Criar mensalidades com valores diferentes
        valores_mensalidade = [150.0, 400.0, 1200.0]
        mensalidades_ids = []
        
        for i, aluno_id in enumerate(alunos_ids):
            mensalidade_id = criar_mensalidade(
                aluno_id, 
                valores_mensalidade[i], 
                date.today(),
                f'Mensalidade {alunos_data[i]["plano"]}'
            )
            mensalidades_ids.append(mensalidade_id)
        
        # Verificar todas as mensalidades
        mensalidades = listar_mensalidades()
        assert len(mensalidades) == 3
        
        # Verificar se todas estão pendentes inicialmente
        for mensalidade in mensalidades:
            assert mensalidade[5] == 'PENDENTE'
        
        # Pagar mensalidade do primeiro aluno
        marcar_mensalidade_paga(mensalidades_ids[0], date.today(), 'Pagamento aluno 1')
        
        # Filtrar por status
        mensalidades_atualizadas = listar_mensalidades()
        pagas = [m for m in mensalidades_atualizadas if m[5] == 'PAGO']
        pendentes = [m for m in mensalidades_atualizadas if m[5] == 'PENDENTE']
        
        assert len(pagas) == 1
        assert len(pendentes) == 2
        assert pagas[0][1] == 'João Santos'  # Nome do aluno que pagou
        
        # Verificar valor total pendente
        total_pendente = sum(m[2] for m in pendentes)
        assert total_pendente == 1600.0  # 400 + 1200
        
        # Verificar valor total pago
        total_pago = sum(m[2] for m in pagas)
        assert total_pago == 150.0


class TestIntegracaoCompleta:
    """Testes de integração para cenários complexos"""
    
    def test_academia_completa_simulacao(self, temp_db):
        """Simulação de academia completa com múltiplas famílias e mensalidades"""
        # Família 1: Responsável + 2 filhos
        responsavel1_id = inserir_aluno(**{
            'nome': 'Ana Souza',
            'cpf': '10000000001',
            'email': 'ana@academia.com',
            'telefone': '11999991111',
            'cep': '01000000',
            'endereco': 'Rua das Flores, 100',
            'data_nasc': '1980-01-01',
            'faixa': 'Preta',
            'grau': '3',
            'peso': '65',
            'altura': '1.68',
            'plano': 'Familiar',
            'foto_path': None,
            'certificado_path': None,
            'biometria_data': None
        })
        
        filho1_id = inserir_aluno(**{
            'nome': 'Bruno Souza',
            'cpf': '10000000002',
            'email': 'bruno@academia.com',
            'telefone': '11999992222',
            'cep': '01000000',
            'endereco': 'Rua das Flores, 100',
            'data_nasc': '2010-06-15',
            'faixa': 'Laranja',
            'grau': '1',
            'peso': '35',
            'altura': '1.30',
            'plano': 'Juvenil',
            'foto_path': None,
            'certificado_path': None,
            'biometria_data': None
        })
        
        kid1_id = inserir_kid(**{
            'nome': 'Carla Souza',
            'cpf': '10000000003',
            'resp_nome': 'Ana Souza',
            'resp_cpf': '10000000001',
            'email': 'carla@academia.com',
            'telefone': '11999993333',
            'cep': '01000000',
            'endereco': 'Rua das Flores, 100',
            'data_nasc': '2015-12-20',
            'faixa': 'Branca',
            'grau': '1',
            'peso': '25',
            'altura': '1.10',
            'plano': 'Kids',
            'foto_path': None,
            'certificado_path': None,
            'biometria_data': None
        })
        
        # Vincular dependentes
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE alunos SET responsavel_id = ? WHERE id = ?", (responsavel1_id, filho1_id))
        conn.commit()
        conn.close()
        
        # Família 2: Casal independente
        aluno_individual_id = inserir_aluno(**{
            'nome': 'Roberto Lima',
            'cpf': '20000000001',
            'email': 'roberto@academia.com',
            'telefone': '11888881111',
            'cep': '02000000',
            'endereco': 'Av. Central, 200',
            'data_nasc': '1995-08-30',
            'faixa': 'Azul',
            'grau': '2',
            'peso': '78',
            'altura': '1.82',
            'plano': 'Mensal',
            'foto_path': None,
            'certificado_path': None,
            'biometria_data': None
        })
        
        # Criar mensalidades para todos
        mensalidades = [
            (responsavel1_id, 250.0, 'Familiar - Responsável'),
            (filho1_id, 120.0, 'Juvenil'),
            (-kid1_id, 80.0, 'Kids'),  # Kids usa ID negativo
            (aluno_individual_id, 150.0, 'Individual')
        ]
        
        mensalidades_ids = []
        for aluno_id, valor, obs in mensalidades:
            msg_id = criar_mensalidade(aluno_id, valor, date.today(), obs)
            mensalidades_ids.append(msg_id)
        
        # Verificar total de mensalidades
        todas_mensalidades = listar_mensalidades()
        assert len(todas_mensalidades) == 4
        
        # Verificar valor total da academia
        receita_total = sum(m[2] for m in todas_mensalidades)
        assert receita_total == 600.0  # 250 + 120 + 80 + 150
        
        # Verificar estrutura familiar
        todos_alunos = listar_todos_alunos()
        
        # Encontrar responsável e verificar dependentes
        responsavel = None
        for aluno in todos_alunos:
            if aluno[0] == responsavel1_id:
                responsavel = aluno
                break
        
        assert responsavel is not None
        assert responsavel[22] == 1  # total_dependentes (só o filho adulto)
        assert 'Bruno Souza' in responsavel[21]  # dependentes_nomes
        
        # Simular alguns pagamentos
        marcar_mensalidade_paga(mensalidades_ids[0], date.today(), 'Responsável pagou')  # Responsável pagou
        marcar_mensalidade_paga(mensalidades_ids[3], date.today(), 'Individual pagou')  # Individual pagou
        
        # Verificar status final
        mensalidades_finais = listar_mensalidades()
        pagas = [m for m in mensalidades_finais if m[5] == 'PAGO']
        pendentes = [m for m in mensalidades_finais if m[5] == 'PENDENTE']
        
        assert len(pagas) == 2
        assert len(pendentes) == 2
        
        receita_paga = sum(m[2] for m in pagas)
        assert receita_paga == 400.0  # 250 + 150
        
        receita_pendente = sum(m[2] for m in pendentes)
        assert receita_pendente == 200.0  # 120 + 80


class TestRobustezSistema:
    """Testes para verificar robustez do sistema"""
    
    def test_dados_invalidos_nao_quebram_sistema(self, temp_db):
        """Teste que dados inválidos não quebram o sistema"""
        # Criar aluno com dados extremos
        aluno_dados_extremos = {
            'nome': 'A' * 200,  # Nome muito longo
            'cpf': '00000000000',  # CPF de zeros
            'email': '',  # Email vazio
            'telefone': '1',  # Telefone muito curto
            'cep': '99999999',  # CEP inválido
            'endereco': '',  # Endereço vazio
            'data_nasc': '1800-01-01',  # Data muito antiga
            'faixa': '',  # Faixa vazia
            'grau': '999',  # Grau inválido
            'peso': '0',  # Peso zero
            'altura': '0',  # Altura zero
            'plano': '',  # Plano vazio
            'foto_path': '/caminho/que/nao/existe.jpg',
            'certificado_path': '/outro/caminho/inexistente.pdf',
            'biometria_data': 'dados_invalidos'
        }
        
        # Sistema deve aceitar dados (validação é feita na UI)
        aluno_id = inserir_aluno(**aluno_dados_extremos)
        assert aluno_id is not None
        
        # Deve aparecer na listagem
        alunos = listar_todos_alunos()
        assert len(alunos) == 1
        
        # Deve permitir criar mensalidade
        mensalidade_id = criar_mensalidade(aluno_id, 0.01, date.today(), '')
        assert mensalidade_id is not None
        
        # Deve aparecer na listagem de mensalidades
        mensalidades = listar_mensalidades()
        assert len(mensalidades) == 1
    
    def test_operacoes_bulk_performance(self, temp_db):
        """Teste performance com muitos registros"""
        import time
        
        start_time = time.time()
        
        # Criar 100 alunos rapidamente
        alunos_ids = []
        for i in range(100):
            aluno_data = {
                'nome': f'Aluno Teste {i:03d}',
                'cpf': f'{i:011d}',
                'email': f'aluno{i:03d}@test.com',
                'telefone': f'11999{i:06d}',
                'cep': f'{i:08d}',
                'endereco': f'Rua {i}, {i}',
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
            
            aluno_id = inserir_aluno(**aluno_data)
            alunos_ids.append(aluno_id)
        
        creation_time = time.time() - start_time
        assert creation_time < 10.0  # Deve criar 100 alunos em menos de 10 segundos
        
        # Criar mensalidades em lote
        start_time = time.time()
        
        for aluno_id in alunos_ids:
            criar_mensalidade(aluno_id, 150.0, date.today(), f'Mensalidade aluno {aluno_id}')
        
        mensalidades_time = time.time() - start_time
        assert mensalidades_time < 5.0  # Deve criar 100 mensalidades em menos de 5 segundos
        
        # Listar todos os dados
        start_time = time.time()
        
        todos_alunos = listar_todos_alunos()
        todas_mensalidades = listar_mensalidades()
        
        query_time = time.time() - start_time
        assert query_time < 2.0  # Deve consultar tudo em menos de 2 segundos
        
        # Verificar integridade dos dados
        assert len(todos_alunos) == 100
        assert len(todas_mensalidades) == 100