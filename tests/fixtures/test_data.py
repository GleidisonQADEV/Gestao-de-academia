"""
Fixtures de dados para testes - Dados de exemplo realistas
"""
from datetime import date, datetime, timedelta
import random


class DataFixtures:
    """Classe com dados fixos para testes"""
    
    @staticmethod
    def get_alunos_adultos():
        """Retorna lista de alunos adultos para testes"""
        return [
            {
                'nome': 'João Silva Santos',
                'cpf': '12345678901',
                'email': 'joao.silva@email.com',
                'telefone': '11999998888',
                'cep': '01310100',
                'endereco': 'Rua Augusta, 1000 - Consolação',
                'data_nasc': '1985-03-15',
                'faixa': 'Azul',
                'grau': '2',
                'peso': '78',
                'altura': '1.80',
                'plano': 'Mensal',
                'foto_path': None,
                'certificado_path': None,
                'biometria_data': None
            },
            {
                'nome': 'Maria Costa Oliveira',
                'cpf': '98765432109',
                'email': 'maria.costa@email.com',
                'telefone': '11888887777',
                'cep': '04038001',
                'endereco': 'Av. Paulista, 1500 - Bela Vista',
                'data_nasc': '1990-07-22',
                'faixa': 'Roxa',
                'grau': '1',
                'peso': '65',
                'altura': '1.68',
                'plano': 'Trimestral',
                'foto_path': None,
                'certificado_path': None,
                'biometria_data': None
            },
            {
                'nome': 'Carlos Eduardo Lima',
                'cpf': '11122233344',
                'email': 'carlos.lima@email.com',
                'telefone': '11777776666',
                'cep': '05415000',
                'endereco': 'Rua Oscar Freire, 800 - Jardins',
                'data_nasc': '1982-11-30',
                'faixa': 'Marrom',
                'grau': '1',
                'peso': '85',
                'altura': '1.85',
                'plano': 'Anual',
                'foto_path': None,
                'certificado_path': None,
                'biometria_data': None
            },
            {
                'nome': 'Ana Paula Rodriguez',
                'cpf': '55566677788',
                'email': 'ana.rodriguez@email.com',
                'telefone': '11666665555',
                'cep': '02011200',
                'endereco': 'Rua do Bosque, 300 - Santana',
                'data_nasc': '1988-05-18',
                'faixa': 'Preta',
                'grau': '2',
                'peso': '62',
                'altura': '1.65',
                'plano': 'Familiar',
                'foto_path': None,
                'certificado_path': None,
                'biometria_data': None
            },
            {
                'nome': 'Roberto Ferreira',
                'cpf': '99988877766',
                'email': 'roberto.ferreira@email.com',
                'telefone': '11555554444',
                'cep': '03058000',
                'endereco': 'Av. Celso Garcia, 2000 - Belém',
                'data_nasc': '1975-12-08',
                'faixa': 'Preta',
                'grau': '4',
                'peso': '90',
                'altura': '1.82',
                'plano': 'Vitalício',
                'foto_path': None,
                'certificado_path': None,
                'biometria_data': None
            }
        ]
    
    @staticmethod
    def get_kids():
        """Retorna lista de crianças para testes"""
        return [
            {
                'nome': 'Pedro Silva Santos',
                'cpf': '12345678902',
                'responsavel': 'João Silva Santos',
                'responsavel_cpf': '12345678901',
                'email': 'pedro.silva@email.com',
                'telefone': '11999998889',
                'cep': '01310100',
                'endereco': 'Rua Augusta, 1000 - Consolação',
                'data_nasc': '2010-08-20',
                'faixa': 'Amarela',
                'grau': '2',
                'peso': '40',
                'altura': '1.45',
                'plano': 'Kids Mensal',
                'foto_path': None,
                'certificado_path': None,
                'biometria_data': None
            },
            {
                'nome': 'Lucas Rodriguez',
                'cpf': '55566677789',
                'responsavel': 'Ana Paula Rodriguez',
                'responsavel_cpf': '55566677788',
                'email': 'lucas.rodriguez@email.com',
                'telefone': '11666665556',
                'cep': '02011200',
                'endereco': 'Rua do Bosque, 300 - Santana',
                'data_nasc': '2012-02-14',
                'faixa': 'Laranja',
                'grau': '1',
                'peso': '35',
                'altura': '1.35',
                'plano': 'Kids Familiar',
                'foto_path': None,
                'certificado_path': None,
                'biometria_data': None
            },
            {
                'nome': 'Sofia Rodriguez',
                'cpf': '55566677790',
                'responsavel': 'Ana Paula Rodriguez',
                'responsavel_cpf': '55566677788',
                'email': 'sofia.rodriguez@email.com',
                'telefone': '11666665557',
                'cep': '02011200',
                'endereco': 'Rua do Bosque, 300 - Santana',
                'data_nasc': '2014-09-05',
                'faixa': 'Vermelha',
                'grau': '1',
                'peso': '28',
                'altura': '1.25',
                'plano': 'Kids Familiar',
                'foto_path': None,
                'certificado_path': None,
                'biometria_data': None
            }
        ]
    
    @staticmethod
    def get_planos():
        """Retorna lista de planos disponíveis"""
        return [
            {'nome': 'Mensal', 'valor': 150.0},
            {'nome': 'Trimestral', 'valor': 400.0},
            {'nome': 'Semestral', 'valor': 750.0},
            {'nome': 'Anual', 'valor': 1200.0},
            {'nome': 'Familiar', 'valor': 280.0},
            {'nome': 'Juvenil', 'valor': 120.0},
            {'nome': 'Kids Mensal', 'valor': 100.0},
            {'nome': 'Kids Familiar', 'valor': 80.0},
            {'nome': 'Vitalício', 'valor': 5000.0},
            {'nome': 'Personalizado', 'valor': 0.0}  # Valor personalizado
        ]
    
    @staticmethod
    def get_faixas_adulto():
        """Retorna lista de faixas para adultos"""
        return [
            'Branca',
            'Azul',
            'Roxa', 
            'Marrom',
            'Preta'
        ]
    
    @staticmethod
    def get_faixas_infantil():
        """Retorna lista de faixas para crianças"""
        return [
            'Branca',
            'Cinza',
            'Amarela',
            'Laranja',
            'Verde',
            'Azul',
            'Roxa',
            'Marrom',
            'Preta'
        ]
    
    @staticmethod
    def generate_mensalidades(alunos_ids, kids_ids=None):
        """Gera dados de mensalidades para os alunos fornecidos"""
        mensalidades = []
        planos_valores = {
            'Mensal': 150.0,
            'Trimestral': 400.0,
            'Semestral': 750.0,
            'Anual': 1200.0,
            'Familiar': 280.0,
            'Juvenil': 120.0,
            'Kids Mensal': 100.0,
            'Kids Familiar': 80.0,
            'Vitalício': 5000.0,
            'Personalizado': 180.0
        }
        
        # Mensalidades para adultos
        for aluno_id in alunos_ids:
            plano = random.choice(list(planos_valores.keys())[:-3])  # Excluir kids e vitalício
            valor = planos_valores[plano]
            
            # Algumas mensalidades vencidas, outras futuras
            dias_offset = random.randint(-30, 30)
            data_vencimento = date.today() + timedelta(days=dias_offset)
            
            mensalidades.append({
                'aluno_id': aluno_id,
                'valor': valor,
                'data_vencimento': data_vencimento,
                'observacoes': f'Mensalidade {plano} - {data_vencimento.strftime("%m/%Y")}'
            })
        
        # Mensalidades para kids (ID negativo)
        if kids_ids:
            for kid_id in kids_ids:
                plano = random.choice(['Kids Mensal', 'Kids Familiar'])
                valor = planos_valores[plano]
                
                dias_offset = random.randint(-15, 45)
                data_vencimento = date.today() + timedelta(days=dias_offset)
                
                mensalidades.append({
                    'aluno_id': -kid_id,  # ID negativo para kids
                    'valor': valor,
                    'data_vencimento': data_vencimento,
                    'observacoes': f'Mensalidade {plano} - {data_vencimento.strftime("%m/%Y")}'
                })
        
        return mensalidades
    
    @staticmethod
    def get_vinculos_familiares():
        """Retorna dados de vínculos familiares de exemplo"""
        return [
            {
                'responsavel_nome': 'Ana Paula Rodriguez',
                'responsavel_cpf': '55566677788',
                'dependentes': [
                    {'nome': 'Lucas Rodriguez', 'cpf': '55566677789', 'tipo': 'kid'},
                    {'nome': 'Sofia Rodriguez', 'cpf': '55566677790', 'tipo': 'kid'}
                ]
            },
            {
                'responsavel_nome': 'João Silva Santos', 
                'responsavel_cpf': '12345678901',
                'dependentes': [
                    {'nome': 'Pedro Silva Santos', 'cpf': '12345678902', 'tipo': 'kid'},
                    {'nome': 'Mariana Silva Santos', 'cpf': '12345678903', 'tipo': 'adulto'}
                ]
            }
        ]
    
    @staticmethod
    def get_cenarios_teste():
        """Retorna cenários específicos para testes"""
        return {
            'academia_pequena': {
                'alunos_adultos': 5,
                'kids': 3,
                'familias': 2,
                'mensalidades_mes': 8
            },
            'academia_media': {
                'alunos_adultos': 25,
                'kids': 15,
                'familias': 8,
                'mensalidades_mes': 40
            },
            'academia_grande': {
                'alunos_adultos': 100,
                'kids': 60,
                'familias': 30,
                'mensalidades_mes': 160
            }
        }
    
    @staticmethod
    def get_dados_invalidos():
        """Retorna dados inválidos para testes de robustez"""
        return [
            {
                'nome': '',  # Nome vazio
                'cpf': '123',  # CPF inválido
                'email': 'email_sem_arroba',  # Email inválido
                'telefone': '1',  # Telefone muito curto
                'cep': '123',  # CEP inválido
                'endereco': '',  # Endereço vazio
                'data_nasc': '2030-01-01',  # Data futura
                'faixa': 'Dourada',  # Faixa inexistente
                'grau': '-1',  # Grau negativo
                'peso': '0',  # Peso zero
                'altura': '0',  # Altura zero
                'plano': 'Inexistente',  # Plano inválido
            },
            {
                'nome': 'A' * 500,  # Nome muito longo
                'cpf': '00000000000',  # CPF de zeros
                'email': 'a' * 100 + '@email.com',  # Email muito longo
                'telefone': '1' * 20,  # Telefone muito longo
                'cep': '00000000',  # CEP de zeros
                'endereco': 'R' * 1000,  # Endereço muito longo
                'data_nasc': '1800-01-01',  # Data muito antiga
                'faixa': 'F' * 50,  # Faixa muito longa
                'grau': '999',  # Grau muito alto
                'peso': '999',  # Peso excessivo
                'altura': '9.99',  # Altura excessiva
                'plano': 'P' * 100,  # Plano muito longo
            }
        ]


class TestDataGenerator:
    """Gerador dinâmico de dados para testes"""
    
    @staticmethod
    def generate_aluno(index=0, **kwargs):
        """Gera dados de aluno com valores únicos"""
        base_data = {
            'nome': f'Aluno Teste {index:03d}',
            'cpf': f'{index:011d}',
            'email': f'aluno{index:03d}@teste.com',
            'telefone': f'11999{index:06d}',
            'cep': f'{index % 100000:05d}000',
            'endereco': f'Rua Teste {index}, {index}',
            'data_nasc': f'{1980 + (index % 40)}-{(index % 12) + 1:02d}-01',
            'faixa': ['Branca', 'Azul', 'Roxa', 'Marrom', 'Preta'][index % 5],
            'grau': str((index % 4) + 1),
            'peso': str(60 + (index % 40)),
            'altura': f'1.{60 + (index % 25)}',
            'plano': ['Mensal', 'Trimestral', 'Anual'][index % 3],
            'foto_path': None,
            'certificado_path': None,
            'biometria_data': None
        }
        
        # Sobrescrever com valores fornecidos
        base_data.update(kwargs)
        return base_data
    
    @staticmethod
    def generate_kid(index=0, responsavel_cpf='12345678901', **kwargs):
        """Gera dados de criança com valores únicos"""
        base_data = {
            'nome': f'Kid Teste {index:03d}',
            'cpf': f'{index + 50000:011d}',
            'responsavel': f'Responsável {index}',
            'responsavel_cpf': responsavel_cpf,
            'email': f'kid{index:03d}@teste.com',
            'telefone': f'11888{index:06d}',
            'cep': f'{index % 100000:05d}000',
            'endereco': f'Rua Kids {index}, {index}',
            'data_nasc': f'{2010 + (index % 10)}-{(index % 12) + 1:02d}-01',
            'faixa': ['Branca', 'Cinza', 'Amarela', 'Laranja', 'Verde'][index % 5],
            'grau': str((index % 3) + 1),
            'peso': str(25 + (index % 20)),
            'altura': f'1.{20 + (index % 30)}',
            'plano': ['Kids Mensal', 'Kids Familiar'][index % 2],
            'foto_path': None,
            'certificado_path': None,
            'biometria_data': None
        }
        
        base_data.update(kwargs)
        return base_data
    
    @staticmethod
    def generate_mensalidade(aluno_id, index=0, **kwargs):
        """Gera dados de mensalidade com valores únicos"""
        base_data = {
            'aluno_id': aluno_id,
            'valor': 150.0 + (index * 10),
            'data_vencimento': date.today() + timedelta(days=index),
            'observacoes': f'Mensalidade teste {index:03d}'
        }
        
        base_data.update(kwargs)
        return base_data