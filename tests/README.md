# 🧪 Sistema de Testes - Legacy BJJ

Sistema completo de testes profissional para garantir a qualidade e robustez do sistema de gestão de academia.

## 📁 Estrutura dos Testes

```
tests/
├── __init__.py                      # Inicialização do módulo de testes
├── conftest.py                      # Configurações globais e fixtures
├── unit/                            # Testes unitários
│   ├── __init__.py
│   ├── test_database.py             # Testes das funções de banco
│   ├── test_ui_components.py        # Testes dos componentes de UI
│   └── test_responsavel_functionality.py  # Testes específicos de responsáveis
├── integration/                     # Testes de integração
│   ├── __init__.py
│   └── test_complete_flows.py       # Testes de fluxos completos
├── fixtures/                        # Dados de exemplo para testes
│   └── test_data.py                 # Fixtures de dados realistas
└── reports/                         # Relatórios gerados (criado automaticamente)
    ├── coverage/                    # Relatório de cobertura HTML
    ├── test_report.html             # Relatório de testes HTML
    └── test_summary.json            # Resumo dos testes em JSON
```

## 🚀 Como Executar os Testes

### Instalação das Dependências

```bash
# Instalar dependências de teste
pip install -r requirements-test.txt

# Ou usar o script que instala automaticamente
python run_tests.py
```

### Opções de Execução

```bash
# Executar todos os testes
python run_tests.py all

# Executar apenas testes unitários
python run_tests.py unit

# Executar apenas testes de integração
python run_tests.py integration

# Executar todos com relatório de cobertura
python run_tests.py coverage

# Executar testes específicos
python run_tests.py specific database
python run_tests.py specific responsavel

# Mostrar ajuda
python run_tests.py help
```

### Usando pytest Diretamente

```bash
# Executar todos os testes
pytest

# Executar testes específicos
pytest tests/unit/test_database.py
pytest tests/integration/
pytest -k "responsavel"

# Com cobertura de código
pytest --cov=src --cov-report=html

# Com relatório HTML
pytest --html=report.html --self-contained-html
```

## 📊 Tipos de Testes

### 🔬 Testes Unitários

Testam funções individuais e componentes isolados:

- **test_database.py**: Operações CRUD do banco de dados
  - Criação/listagem/atualização de alunos
  - Gestão de mensalidades
  - Operações de kids
  - Funcionalidade de responsáveis/dependentes
  - Validações de dados

- **test_ui_components.py**: Componentes de interface
  - Diálogos personalizados
  - Validações de formulários
  - Formatação de dados (CPF, telefone, CEP)
  - Funcionalidade de vincular responsável

- **test_responsavel_functionality.py**: Funcionalidades específicas
  - Vinculação responsável-dependente
  - Listagem de vínculos familiares
  - Desvinculação
  - Cenários complexos de famílias

### 🔗 Testes de Integração

Testam fluxos completos e interação entre componentes:

- **test_complete_flows.py**: Cenários end-to-end
  - Ciclo completo de gestão de alunos
  - Fluxos financeiros complexos
  - Gestão familiar completa
  - Simulação de academia real
  - Testes de performance e robustez

### 🎯 Fixtures e Dados de Teste

- **test_data.py**: Dados realistas para testes
  - Alunos adultos e crianças
  - Famílias com múltiplos dependentes
  - Planos e mensalidades variados
  - Cenários de academias (pequena, média, grande)
  - Dados inválidos para testes de robustez

## 📈 Relatórios e Cobertura

### Relatório de Cobertura
- **Localização**: `tests/reports/coverage/index.html`
- **Conteúdo**: Porcentagem de código coberto por testes
- **Meta**: Manter acima de 80%

### Relatório de Testes
- **Localização**: `tests/reports/test_report.html`
- **Conteúdo**: Resultados detalhados de todos os testes
- **Informações**: Tempo de execução, falhas, sucessos

### Resumo JSON
- **Localização**: `tests/reports/test_summary.json`
- **Conteúdo**: Metadados dos testes executados
- **Uso**: Integração com CI/CD

## 🔧 Configuração

### pytest.ini
```ini
[tool:pytest]
addopts = -v --strict-markers --tb=short --durations=10 --color=yes
testpaths = tests
markers =
    unit: Testes unitários
    integration: Testes de integração
    slow: Testes que demoram para executar
    database: Testes que dependem do banco de dados
    ui: Testes de interface
    responsavel: Testes específicos de responsáveis
```

### Fixtures Principais

- **temp_db**: Banco de dados temporário para cada teste
- **sample_aluno_data**: Dados de exemplo para aluno adulto
- **sample_kid_data**: Dados de exemplo para criança
- **sample_mensalidade_data**: Dados de exemplo para mensalidade
- **mock_qt_widgets**: Mocks para componentes Qt

## ⚡ Execução Rápida

Para desenvolvimento ágil, use estes comandos:

```bash
# Teste rápido após mudanças
pytest tests/unit/ -x -v

# Teste específico que você está desenvolvendo
pytest tests/unit/test_responsavel_functionality.py::TestResponsavelFunctionality::test_vincular_dependente_adulto -v

# Teste com debug (mostra prints)
pytest tests/unit/test_database.py -s

# Teste paralelo (mais rápido)
pytest -n auto
```

## 🎯 Boas Práticas

### Para Desenvolvedores

1. **Execute testes antes de commit**
   ```bash
   python run_tests.py all
   ```

2. **Escreva testes para novas funcionalidades**
   - Crie teste antes de implementar (TDD)
   - Cubra casos de erro e edge cases
   - Use nomes descritivos para testes

3. **Mantenha testes independentes**
   - Cada teste deve poder executar sozinho
   - Use fixtures para dados compartilhados
   - Limpe estado após cada teste

4. **Documente testes complexos**
   - Explique o cenário sendo testado
   - Documente dados de entrada esperados
   - Comente asserções não óbvias

### Padrões de Nomenclatura

```python
class TestFuncionalidade:
    def test_cenario_esperado_resultado(self):
        # Arrange (preparar dados)
        dados = {...}
        
        # Act (executar ação)
        resultado = funcao(dados)
        
        # Assert (verificar resultado)
        assert resultado == esperado
```

## 🚨 Cenários de Teste Críticos

### Funcionalidades Essenciais Testadas

1. **Gestão de Alunos**
   - ✅ Criação com dados válidos/inválidos
   - ✅ Listagem e filtros
   - ✅ Atualização de informações
   - ✅ Inativação/reativação

2. **Sistema Financeiro**
   - ✅ Criação de mensalidades
   - ✅ Marcação de pagamentos
   - ✅ Relatórios financeiros
   - ✅ Filtros por status

3. **Vínculos Familiares**
   - ✅ Vinculação responsável-dependente
   - ✅ Múltiplos dependentes
   - ✅ Desvinculação
   - ✅ Consultas com vínculos

4. **Robustez do Sistema**
   - ✅ Dados inválidos não quebram sistema
   - ✅ Performance com muitos registros
   - ✅ Integridade de dados mantida
   - ✅ Recuperação de erros

## 📝 Adicionando Novos Testes

### Para Nova Funcionalidade

1. **Criar arquivo de teste**
   ```python
   # tests/unit/test_nova_funcionalidade.py
   import pytest
   
   class TestNovaFuncionalidade:
       def test_caso_basico(self, temp_db):
           # Seu teste aqui
           pass
   ```

2. **Adicionar fixture se necessário**
   ```python
   # Em conftest.py
   @pytest.fixture
   def dados_especificos():
       return {"chave": "valor"}
   ```

3. **Executar e verificar**
   ```bash
   pytest tests/unit/test_nova_funcionalidade.py -v
   ```

### Para Teste de Integração

1. **Criar cenário complexo**
   ```python
   # tests/integration/test_novo_fluxo.py
   def test_fluxo_completo(self, temp_db):
       # 1. Preparar dados
       # 2. Executar sequência de ações
       # 3. Verificar estado final
   ```

2. **Usar dados realistas**
   ```python
   from tests.fixtures.test_data import DataFixtures
   
   dados = DataFixtures.get_alunos_adultos()
   ```

## 📞 Suporte e Manutenção

### Problemas Comuns

**Testes Falhando Após Mudanças**
- Verifique se mudou assinatura de funções
- Atualize assertions se mudou retornos
- Execute `python run_tests.py coverage` para ver cobertura

**Banco de Dados Bloqueado**
- Certifique que não há processo usando o banco
- Use fixture `temp_db` para isolamento

**Imports Não Funcionam**
- Verifique `sys.path` em conftest.py
- Execute testes a partir da raiz do projeto

### Melhorias Futuras

- [ ] Testes de carga automatizados
- [ ] Integração com CI/CD
- [ ] Testes de interface gráfica
- [ ] Testes de API (se implementada)
- [ ] Benchmarks de performance

---

## 🏆 Benefícios do Sistema de Testes

✅ **Confiabilidade**: Detecta bugs antes da produção  
✅ **Manutenibilidade**: Facilita refatorações seguras  
✅ **Documentação**: Testes servem como documentação viva  
✅ **Qualidade**: Força código melhor estruturado  
✅ **Produtividade**: Reduz tempo de debug manual  

**Execute os testes regularmente e mantenha a qualidade sempre alta!** 🥋