"""
Testes específicos para funcionalidade de responsáveis e dependentes
"""
import pytest
from database.db import (
    inserir_aluno, listar_todos_alunos, criar_mensalidade, 
    listar_mensalidades, get_conn
)
from datetime import date


class TestResponsavelFunctionality:
    """Testes específicos para funcionalidade de responsáveis"""
    
    def test_responsavel_sem_dependentes(self, temp_db):
        """Teste aluno responsável sem dependentes"""
        # Criar aluno que será responsável
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
            'plano': 'Familiar',
            'foto_path': None,
            'certificado_path': None,
            'biometria_data': None
        }
        
        responsavel_id = inserir_aluno(**responsavel_data)
        
        # Verificar na listagem
        todos_alunos = listar_todos_alunos()
        responsavel = None
        
        for aluno in todos_alunos:
            if aluno[0] == responsavel_id:
                responsavel = aluno
                break
        
        assert responsavel is not None
        # Deve ter 0 dependentes
        assert responsavel[22] == 0  # total_dependentes
        assert responsavel[21] is None or responsavel[21] == ''  # dependentes_nomes
        # Não deve ter responsável
        assert responsavel[19] is None  # responsavel_nome
        assert responsavel[20] is None  # responsavel_cpf
    
    def test_vincular_dependente_adulto(self, temp_db):
        """Teste vinculação de dependente adulto ao responsável"""
        # Criar responsável
        responsavel_data = {
            'nome': 'Maria Silva',
            'cpf': '11111111111',
            'email': 'maria@test.com',
            'telefone': '11999999999',
            'cep': '01234567',
            'endereco': 'Rua Teste, 123',
            'data_nasc': '1975-01-01',
            'faixa': 'Preta',
            'grau': '2',
            'peso': '65',
            'altura': '1.68',
            'plano': 'Familiar',
            'foto_path': None,
            'certificado_path': None,
            'biometria_data': None
        }
        
        # Criar dependente
        dependente_data = {
            'nome': 'Ana Silva',
            'cpf': '22222222222',
            'email': 'ana@test.com',
            'telefone': '11888888888',
            'cep': '01234567',
            'endereco': 'Rua Teste, 123',
            'data_nasc': '2005-01-01',
            'faixa': 'Azul',
            'grau': '1',
            'peso': '55',
            'altura': '1.65',
            'plano': 'Juvenil',
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
        responsavel = None
        dependente = None
        
        for aluno in todos_alunos:
            if aluno[0] == responsavel_id:
                responsavel = aluno
            elif aluno[0] == dependente_id:
                dependente = aluno
        
        # Verificar responsável
        assert responsavel is not None
        assert responsavel[22] == 1  # total_dependentes
        assert 'Ana Silva' in responsavel[21]  # dependentes_nomes
        
        # Verificar dependente
        assert dependente is not None
        assert dependente[19] == 'Maria Silva'  # responsavel_nome
        assert dependente[20] == '11111111111'  # responsavel_cpf
    
    def test_multiplos_dependentes(self, temp_db):
        """Teste responsável com múltiplos dependentes"""
        # Criar responsável
        responsavel_data = {
            'nome': 'Carlos Silva',
            'cpf': '33333333333',
            'email': 'carlos@test.com',
            'telefone': '11999999999',
            'cep': '01234567',
            'endereco': 'Rua Família, 456',
            'data_nasc': '1970-01-01',
            'faixa': 'Preta',
            'grau': '3',
            'peso': '80',
            'altura': '1.80',
            'plano': 'Familiar',
            'foto_path': None,
            'certificado_path': None,
            'biometria_data': None
        }
        
        # Criar 3 dependentes
        dependentes_data = [
            {
                'nome': 'Pedro Silva',
                'cpf': '44444444444',
                'email': 'pedro@test.com',
                'telefone': '11888888881',
                'cep': '01234567',
                'endereco': 'Rua Família, 456',
                'data_nasc': '2000-01-01',
                'faixa': 'Roxa',
                'grau': '1',
                'peso': '70',
                'altura': '1.75',
                'plano': 'Juvenil',
                'foto_path': None,
                'certificado_path': None,
                'biometria_data': None
            },
            {
                'nome': 'Lucia Silva',
                'cpf': '55555555555',
                'email': 'lucia@test.com',
                'telefone': '11888888882',
                'cep': '01234567',
                'endereco': 'Rua Família, 456',
                'data_nasc': '2003-01-01',
                'faixa': 'Azul',
                'grau': '2',
                'peso': '60',
                'altura': '1.68',
                'plano': 'Juvenil',
                'foto_path': None,
                'certificado_path': None,
                'biometria_data': None
            },
            {
                'nome': 'Roberto Silva',
                'cpf': '66666666666',
                'email': 'roberto@test.com',
                'telefone': '11888888883',
                'cep': '01234567',
                'endereco': 'Rua Família, 456',
                'data_nasc': '2008-01-01',
                'faixa': 'Verde',
                'grau': '1',
                'peso': '50',
                'altura': '1.60',
                'plano': 'Juvenil',
                'foto_path': None,
                'certificado_path': None,
                'biometria_data': None
            }
        ]
        
        responsavel_id = inserir_aluno(**responsavel_data)
        dependentes_ids = []
        
        for dep_data in dependentes_data:
            dep_id = inserir_aluno(**dep_data)
            dependentes_ids.append(dep_id)
        
        # Vincular todos os dependentes
        conn = get_conn()
        cur = conn.cursor()
        for dep_id in dependentes_ids:
            cur.execute("UPDATE alunos SET responsavel_id = ? WHERE id = ?", (responsavel_id, dep_id))
        conn.commit()
        conn.close()
        
        # Verificar vinculações
        todos_alunos = listar_todos_alunos()
        responsavel = None
        
        for aluno in todos_alunos:
            if aluno[0] == responsavel_id:
                responsavel = aluno
                break
        
        assert responsavel is not None
        assert responsavel[22] == 3  # total_dependentes
        
        # Verificar se todos os nomes estão na lista
        dependentes_nomes = responsavel[21]
        assert 'Pedro Silva' in dependentes_nomes
        assert 'Lucia Silva' in dependentes_nomes
        assert 'Roberto Silva' in dependentes_nomes
    
    def test_mensalidades_familia_completa(self, temp_db):
        """Teste mensalidades para família completa"""
        # Criar responsável
        responsavel_id = inserir_aluno(**{
            'nome': 'Patricia Costa',
            'cpf': '77777777777',
            'email': 'patricia@test.com',
            'telefone': '11999999999',
            'cep': '01234567',
            'endereco': 'Av. Família, 789',
            'data_nasc': '1985-01-01',
            'faixa': 'Marrom',
            'grau': '1',
            'peso': '62',
            'altura': '1.65',
            'plano': 'Familiar',
            'foto_path': None,
            'certificado_path': None,
            'biometria_data': None
        })
        
        # Criar dependente
        dependente_id = inserir_aluno(**{
            'nome': 'Gabriel Costa',
            'cpf': '88888888888',
            'email': 'gabriel@test.com',
            'telefone': '11888888888',
            'cep': '01234567',
            'endereco': 'Av. Família, 789',
            'data_nasc': '2010-01-01',
            'faixa': 'Amarela',
            'grau': '1',
            'peso': '40',
            'altura': '1.45',
            'plano': 'Kids',
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
        
        # Criar mensalidades para ambos
        msg1_id = criar_mensalidade(responsavel_id, 280.0, date.today(), 'Plano Familiar')
        msg2_id = criar_mensalidade(dependente_id, 100.0, date.today(), 'Plano Kids')
        
        # Verificar mensalidades na listagem (apenas responsáveis devem aparecer)
        mensalidades = listar_mensalidades()
        assert len(mensalidades) == 1  # Apenas o responsável deve aparecer

        assert mensalidades[0][1] == 'Patricia Costa'  # Nome do responsável
        assert mensalidades[0][2] == 280.0  # Valor da mensalidade do responsável
    
    def test_desvincular_dependente(self, temp_db):
        """Teste desvinculação de dependente"""
        # Criar responsável e dependente
        responsavel_id = inserir_aluno(**{
            'nome': 'Eduardo Santos',
            'cpf': '99999999999',
            'email': 'eduardo@test.com',
            'telefone': '11999999999',
            'cep': '01234567',
            'endereco': 'Rua Teste, 999',
            'data_nasc': '1990-01-01',
            'faixa': 'Azul',
            'grau': '1',
            'peso': '75',
            'altura': '1.78',
            'plano': 'Mensal',
            'foto_path': None,
            'certificado_path': None,
            'biometria_data': None
        })
        
        dependente_id = inserir_aluno(**{
            'nome': 'Felipe Santos',
            'cpf': '10101010101',
            'email': 'felipe@test.com',
            'telefone': '11888888888',
            'cep': '01234567',
            'endereco': 'Rua Teste, 999',
            'data_nasc': '2012-01-01',
            'faixa': 'Branca',
            'grau': '1',
            'peso': '35',
            'altura': '1.40',
            'plano': 'Kids',
            'foto_path': None,
            'certificado_path': None,
            'biometria_data': None
        })
        
        # Vincular
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE alunos SET responsavel_id = ? WHERE id = ?", (responsavel_id, dependente_id))
        conn.commit()
        
        # Verificar vinculação
        todos_alunos = listar_todos_alunos()
        responsavel = next((a for a in todos_alunos if a[0] == responsavel_id), None)
        dependente = next((a for a in todos_alunos if a[0] == dependente_id), None)
        
        assert responsavel[22] == 1  # tem dependente
        assert dependente[19] == 'Eduardo Santos'  # tem responsável
        
        # Desvincular
        cur.execute("UPDATE alunos SET responsavel_id = NULL WHERE id = ?", (dependente_id,))
        conn.commit()
        conn.close()
        
        # Verificar desvinculação
        todos_alunos_atualizado = listar_todos_alunos()
        responsavel_atualizado = next((a for a in todos_alunos_atualizado if a[0] == responsavel_id), None)
        dependente_atualizado = next((a for a in todos_alunos_atualizado if a[0] == dependente_id), None)
        
        assert responsavel_atualizado[22] == 0  # não tem mais dependente
        assert dependente_atualizado[19] is None  # não tem mais responsável
    
    def test_busca_responsavel_por_cpf(self, temp_db):
        """Teste busca de responsável por CPF (simula funcionalidade do UI)"""
        # Criar vários alunos
        alunos_data = [
            {'nome': 'Aluno 1', 'cpf': '11111111111', 'email': 'a1@test.com'},
            {'nome': 'Aluno 2', 'cpf': '22222222222', 'email': 'a2@test.com'},
            {'nome': 'Maria Responsável', 'cpf': '33333333333', 'email': 'maria@test.com'},
            {'nome': 'Aluno 4', 'cpf': '44444444444', 'email': 'a4@test.com'},
        ]
        
        alunos_ids = []
        for dados in alunos_data:
            # Completar dados obrigatórios
            dados.update({
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
            })
            aluno_id = inserir_aluno(**dados)
            alunos_ids.append(aluno_id)
        
        # Simular busca por CPF (como faria a UI)
        cpf_busca = '33333333333'
        
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, nome FROM alunos WHERE cpf = ? AND ativo = 1", (cpf_busca,))
        resultado = cur.fetchone()
        conn.close()
        
        assert resultado is not None
        assert resultado[1] == 'Maria Responsável'
        
        # CPF inexistente - Nova conexão
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, nome FROM alunos WHERE cpf = ? AND ativo = 1", ('99999999999',))
        resultado_inexistente = cur.fetchone()
        conn.close()
        
        assert resultado_inexistente is None
    
    def test_validacao_cpf_formato(self):
        """Teste validação de formato de CPF (simula validação da UI)"""
        def limpar_cpf(cpf_str):
            """Função que simula limpeza de CPF na UI"""
            return ''.join(filter(str.isdigit, cpf_str.strip()))
        
        def validar_cpf(cpf_limpo):
            """Função que simula validação de CPF na UI"""
            return len(cpf_limpo) == 11
        
        # Testes de formatação
        assert limpar_cpf('123.456.789-01') == '12345678901'
        assert limpar_cpf('12345678901') == '12345678901'
        assert limpar_cpf('123-456-789-01') == '12345678901'
        assert limpar_cpf('  123 456 789 01  ') == '12345678901'
        
        # Testes de validação
        assert validar_cpf('12345678901') is True
        assert validar_cpf('123456789') is False  # Muito curto
        assert validar_cpf('123456789012') is False  # Muito longo
        assert validar_cpf('') is False  # Vazio
    
    def test_cenario_academia_real(self, temp_db):
        """Teste cenário realista de academia com famílias"""
        # Família 1: Mãe + 2 filhos
        mae1_id = inserir_aluno(**{
            'nome': 'Sandra Oliveira',
            'cpf': '12345678901',
            'email': 'sandra@academia.com',
            'telefone': '11999991111',
            'cep': '01000000',
            'endereco': 'Rua das Acácias, 100',
            'data_nasc': '1982-03-15',
            'faixa': 'Azul',
            'grau': '2',
            'peso': '68',
            'altura': '1.68',
            'plano': 'Familiar',
            'foto_path': None,
            'certificado_path': None,
            'biometria_data': None
        })
        
        filho1_id = inserir_aluno(**{
            'nome': 'João Oliveira',
            'cpf': '12345678902',
            'email': 'joao.o@academia.com',
            'telefone': '11999992222',
            'cep': '01000000',
            'endereco': 'Rua das Acácias, 100',
            'data_nasc': '2008-08-20',
            'faixa': 'Verde',
            'grau': '1',
            'peso': '45',
            'altura': '1.55',
            'plano': 'Juvenil',
            'foto_path': None,
            'certificado_path': None,
            'biometria_data': None
        })
        
        filho2_id = inserir_aluno(**{
            'nome': 'Maria Oliveira',
            'cpf': '12345678903',
            'email': 'maria.o@academia.com',
            'telefone': '11999993333',
            'cep': '01000000',
            'endereco': 'Rua das Acácias, 100',
            'data_nasc': '2012-12-05',
            'faixa': 'Amarela',
            'grau': '1',
            'peso': '35',
            'altura': '1.40',
            'plano': 'Kids',
            'foto_path': None,
            'certificado_path': None,
            'biometria_data': None
        })
        
        # Família 2: Pai + 1 filho
        pai2_id = inserir_aluno(**{
            'nome': 'Ricardo Santos',
            'cpf': '98765432101',
            'email': 'ricardo@academia.com',
            'telefone': '11888881111',
            'cep': '02000000',
            'endereco': 'Av. Central, 200',
            'data_nasc': '1978-11-22',
            'faixa': 'Marrom',
            'grau': '1',
            'peso': '82',
            'altura': '1.80',
            'plano': 'Anual',
            'foto_path': None,
            'certificado_path': None,
            'biometria_data': None
        })
        
        filho3_id = inserir_aluno(**{
            'nome': 'Carlos Santos',
            'cpf': '98765432102',
            'email': 'carlos.s@academia.com',
            'telefone': '11888882222',
            'cep': '02000000',
            'endereco': 'Av. Central, 200',
            'data_nasc': '2006-04-10',
            'faixa': 'Azul',
            'grau': '1',
            'peso': '55',
            'altura': '1.65',
            'plano': 'Juvenil',
            'foto_path': None,
            'certificado_path': None,
            'biometria_data': None
        })
        
        # Vincular dependentes
        conn = get_conn()
        cur = conn.cursor()
        
        # Família 1
        cur.execute("UPDATE alunos SET responsavel_id = ? WHERE id = ?", (mae1_id, filho1_id))
        cur.execute("UPDATE alunos SET responsavel_id = ? WHERE id = ?", (mae1_id, filho2_id))
        
        # Família 2
        cur.execute("UPDATE alunos SET responsavel_id = ? WHERE id = ?", (pai2_id, filho3_id))
        
        conn.commit()
        conn.close()
        
        # Criar mensalidades para todas as famílias
        mensalidades = [
            (mae1_id, 250.0, 'Plano Familiar - Sandra'),
            (filho1_id, 120.0, 'Plano Juvenil - João'),
            (filho2_id, 100.0, 'Plano Kids - Maria'),
            (pai2_id, 1200.0, 'Plano Anual - Ricardo'),
            (filho3_id, 120.0, 'Plano Juvenil - Carlos')
        ]
        
        for aluno_id, valor, obs in mensalidades:
            criar_mensalidade(aluno_id, valor, date.today(), obs)
        
        # Verificar estrutura familiar final
        todos_alunos = listar_todos_alunos()
        
        # Verificar responsáveis
        mae1 = next((a for a in todos_alunos if a[0] == mae1_id), None)
        pai2 = next((a for a in todos_alunos if a[0] == pai2_id), None)
        
        assert mae1[22] == 2  # Sandra tem 2 dependentes
        assert 'João Oliveira' in mae1[21] and 'Maria Oliveira' in mae1[21]
        
        assert pai2[22] == 1  # Ricardo tem 1 dependente
        assert 'Carlos Santos' in pai2[21]
        
        # Verificar dependentes
        filho1 = next((a for a in todos_alunos if a[0] == filho1_id), None)
        filho2 = next((a for a in todos_alunos if a[0] == filho2_id), None)
        filho3 = next((a for a in todos_alunos if a[0] == filho3_id), None)
        
        assert filho1[19] == 'Sandra Oliveira'
        assert filho2[19] == 'Sandra Oliveira'
        assert filho3[19] == 'Ricardo Santos'
        
        # Verificar mensalidades totais (apenas responsáveis devem aparecer na listagem)
        mensalidades_total = listar_mensalidades()
        assert len(mensalidades_total) == 2  # Apenas Sandra e Ricardo (responsáveis)

        receita_total = sum(m[2] for m in mensalidades_total)
        assert receita_total == 1450.0  # 250 (Sandra) + 1200 (Ricardo) - dependentes não aparecem na listagem