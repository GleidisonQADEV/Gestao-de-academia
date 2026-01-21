"""
Testes para funcionalidade de métricas de frequência e presença
"""

import pytest
import database.db as db


class TestFrequenciaMetrics:
    """
    Testes para sistema de métricas de frequência
    """

    def test_obter_metricas_frequencia_estrutura_basica(self):
        """
        Testa se a função obter_metricas_frequencia retorna estrutura correta
        """
        # Act
        metricas = db.obter_metricas_frequencia()
        
        # Assert
        assert metricas is not None, "Deve retornar estrutura de métricas"
        assert isinstance(metricas, dict), "Métricas devem ser um dicionário"
        
        # Verificar estrutura atual do retorno
        assert 'frequencia' in metricas, "Deve conter seção de frequência"
        freq = metricas['frequencia']
        
        assert isinstance(freq['frequencia_horarios'], dict), "Frequência por horário deve ser dict"
        assert 'alunos_ativos_periodo' in freq, "Deve conter alunos ativos no período"
        assert 'dias_periodo' in freq, "Deve conter dias do período"
        assert 'eh_dia_aula' in freq, "Deve indicar se hoje é dia de aula"
    
    def test_registrar_presenca_funcao_existe(self):
        """
        Testa se a função registrar_presenca existe e é chamável
        """
        # Verificar se função existe
        assert hasattr(db, 'registrar_presenca'), "Função registrar_presenca deve existir"
        assert callable(db.registrar_presenca), "registrar_presenca deve ser chamável"
    
    def test_registrar_presenca_aluno_inexistente(self):
        """
        Testa comportamento com aluno inexistente - verifica estrutura do retorno
        """
        # Teste básico com aluno inexistente
        resultado = db.registrar_presenca(999999)  # ID inexistente
        
        # A função retorna uma tupla (success, message)
        assert isinstance(resultado, tuple), "Deve retornar tupla (success, message)"
        assert len(resultado) == 2, "Tupla deve ter 2 elementos"
        
        success, message = resultado
        assert isinstance(success, bool), "Primeiro elemento deve ser boolean"
        assert isinstance(message, str), "Segundo elemento deve ser string"
    
    def test_horarios_aula_definidos(self):
        """
        Testa se os horários de aula estão definidos corretamente nas métricas
        """
        # Act
        metricas = db.obter_metricas_frequencia()
        
        # Assert
        freq = metricas['frequencia']
        horarios = freq['frequencia_horarios']
        
        # Verificar se contém os horários esperados
        horarios_esperados = ['08:30:00', '12:00:00', '18:30:00', '19:30:00']
        for horario in horarios_esperados:
            assert horario in horarios, f"Deve conter horário {horario}"
            assert isinstance(horarios[horario], int), f"Frequência do horário {horario} deve ser inteiro"