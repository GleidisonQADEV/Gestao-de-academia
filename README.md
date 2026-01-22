# 🥋 Sistema de Gestão de Academia - Legacy BJJ

Sistema desktop completo em Python para gestão integrada de academia de jiu-jitsu, com controle de alunos, mensalidades, presença e relatórios financeiros.

## 🚀 Como executar a aplicação

### Método 1: Usando o script de execução (Recomendado)
```bash
./run.sh
```

### Método 2: Manual
```bash
# Ativar o ambiente virtual
source venv/bin/activate

# Executar a aplicação
python3 src/main.py
```

## 🔐 Credenciais de Acesso

- **Usuário:** `admin`
- **Senha:** `senha`

## 🎯 Funcionalidades Principais

### 👥 Gestão de Alunos
- **Cadastro completo** de alunos adultos e kids
- **Sistema de responsáveis** e dependentes com vinculação automática
- **Pesquisa avançada** por nome, CPF ou responsável
- **Gestão de status** (ativo/inativo) com histórico
- **Upload de fotos** e certificados
- **Sistema de biometria** (integração preparada)
- **Validação robusta** de CPF, e-mail e dados únicos

### 👶 Gestão de Kids
- Módulo especializado para alunos infantis (5-13 anos)
- Cadastro de responsáveis obrigatório
- CPF opcional para menores
- Vinculação automática com mensalidades dos responsáveis
- Geração automática de mensalidades quando aplicável

### 💰 Sistema Financeiro
- **Geração automática** de mensalidades mensais e anuais
- **Controle de vencimentos** com alertas de atraso
- **Gestão de planos** personalizáveis com valores flexíveis
- **Dashboard financeiro** com métricas em tempo real
- **Relatórios de pagamento** em PDF
- **Status de pagamento** (Pendente, Pago, Atrasado)

### 📊 Dashboard e Métricas
- **Métricas de alunos** (ativos, inativos, total)
- **Indicadores financeiros** (receita, inadimplência)
- **Análise de frequência** por período
- **Gráficos visuais** de performance

### 🏃‍♂️ Controle de Presença
- **Registro de entrada e saída** por horário de aula
- **Métricas de frequência** considerando apenas dias de aula
- **Histórico de presenças** por aluno
- **Relatórios de frequência** personalizados

### 📋 Gestão de Planos
- **Planos pré-configurados** (Adulto, Kids, Família)
- **Criação de planos personalizados**
- **Planos especiais** (Bolsista, Vinculado ao responsável)
- **Controle de ativação/desativação**
- **Valores flexíveis** por categoria

### 🔍 Sistema de Busca
- **Pesquisa específica:** Nome, CPF ou responsável
- **Listar todos:** Visualização completa em grid
- **Resultados em cards** com design otimizado
- **Ordenação alfabética** automática

### 🎨 Interface Moderna
- **Design responsivo** com PySide6
- **Cards transparentes** com campos destacados
- **Layout otimizado** para diferentes resoluções
- **Navegação por abas** intuitiva
- **Temas customizáveis** via CSS

## 🛠 Tecnologias

### Core
- **Python 3.10+** - Linguagem principal
- **PySide6** - Interface gráfica moderna
- **SQLite** - Banco de dados local

### Desenvolvimento
- **pytest** - Framework de testes com 93+ testes
- **pytest-cov** - Cobertura de código
- **pytest-html** - Relatórios HTML
- **pytest-mock** - Mocking para testes

### Estrutura
- **MVC Pattern** - Separação clara de responsabilidades
- **Modularização** - Código organizado por funcionalidades
- **Testes abrangentes** - Unitários e de integração

## 🏗 Estrutura Completa do Projeto

```
📁 Gestao-de-academia/
├── 📄 README.md                    # Documentação principal
├── 📄 requirements.txt             # Dependências de produção
├── 📄 requirements-test.txt        # Dependências de teste
├── 📄 pytest.ini                  # Configurações de teste
├── 📄 PROTOCOLO_DESENVOLVIMENTO.md # Guia de desenvolvimento
├── 📄 LegacyBJJ.spec              # Configuração PyInstaller
├── 🔧 run.sh                       # Script de execução
├── 🔧 t.sh                         # Script de testes
├── 🗑  limpar_banco.py             # Utilitário limpeza BD

├── 📁 src/                         # Código fonte principal
│   ├── 🚀 main.py                  # Aplicação principal
│   ├── 📁 assets/                  # Recursos estáticos
│   │   └── 🖼  logo.png            # Logo da academia
│   │
│   ├── 📁 database/                # Camada de dados
│   │   ├── 🔧 __init__.py
│   │   ├── 💾 db.py                # Banco principal (adultos)
│   │   └── 👶 kids_db.py           # Banco kids especializado
│   │
│   ├── 📁 services/                # Lógica de negócio
│   │   └── (módulos de serviço)
│   │
│   ├── 📁 ui/                      # Interface do usuário
│   │   ├── 🏠 login_window.py      # Tela de autenticação
│   │   ├── 👥 alunos_tab.py        # Visualização de alunos
│   │   ├── ➕ cadastro_aluno_tab.py # Cadastro de alunos
│   │   ├── 📊 dashboard_tab.py     # Dashboard principal
│   │   ├── 💰 financeiro_tab.py    # Gestão financeira
│   │   ├── ⚠️  alertas_tab.py       # Sistema de alertas
│   │   ├── ⚙️  config_tab.py       # Configurações
│   │   ├── 👤 aluno_profile.py     # Perfil detalhado
│   │   ├── 📋 base_tab.py          # Classe base para abas
│   │   ├── 💬 app_dialog.py        # Diálogos da aplicação
│   │   ├── 🔒 change_password_dialog.py # Alteração de senha
│   │   ├── 📜 historico_dialog.py  # Histórico de ações
│   │   └── 🎨 style.qss            # Estilos CSS
│   │
│   └── 📁 utils/                   # Utilitários
│       ├── 📄 pdf_report.py        # Geração de relatórios PDF
│       └── 🔗 vincular_utils.py    # Utilitários de vinculação

├── 📁 tests/                       # Suite de testes (93+ testes)
│   ├── 🔧 __init__.py
│   ├── ⚙️  conftest.py             # Configurações pytest
│   │
│   ├── 📁 fixtures/                # Dados de teste
│   │   └── 📊 test_data.py         # Fixtures compartilhadas
│   │
│   ├── 📁 unit/                    # Testes unitários
│   │   ├── 🧪 test_auth_and_init.py      # Autenticação
│   │   ├── 📊 test_dashboard_*.py        # Dashboard
│   │   ├── 💾 test_database.py           # Operações BD
│   │   ├── 👥 test_alunos_*.py           # Funcionalidades alunos
│   │   ├── 💰 test_mensalidades_*.py     # Sistema financeiro
│   │   ├── 👨‍👩‍👧‍👦 test_responsavel_*.py    # Sistema responsáveis
│   │   ├── 📈 test_frequencia_*.py       # Controle presença
│   │   ├── 🎨 test_ui_components.py      # Componentes UI
│   │   └── 🔧 test_utils_functions.py    # Funções utilitárias
│   │
│   └── 📁 integration/             # Testes de integração
│       └── 🔄 test_complete_flows.py # Fluxos completos

└── 📁 build/                       # Arquivos de build
    └── 📁 LegacyBJJ/              # Build PyInstaller
        └── (arquivos de distribuição)
```

## 🗃 Estrutura do Banco de Dados

### Tabelas Principais
- **`users`** - Sistema de autenticação
- **`alunos`** - Alunos adultos com responsáveis
- **`kids`** - Alunos infantis especializados
- **`mensalidades`** - Controle financeiro
- **`planos`** - Gestão de planos de pagamento
- **`registros_presenca`** - Controle de frequência

### Relacionamentos
- Alunos ↔ Responsáveis (1:N)
- Alunos ↔ Mensalidades (1:N)
- Alunos ↔ Registros de Presença (1:N)
- Planos ↔ Alunos (1:N)

## 🧪 Sistema de Testes

### Cobertura Completa
- **93+ testes automatizados**
- **Testes unitários** para cada módulo
- **Testes de integração** para fluxos completos
- **Testes de UI** para componentes visuais
- **Testes de banco de dados** para operações CRUD

### Executar Testes
```bash
# Executar todos os testes
./t.sh

# Executar testes específicos
pytest tests/unit/test_database.py -v

# Gerar relatório de cobertura
pytest --cov=src --cov-report=html
```

## 🔄 Ambiente Virtual

O projeto utiliza isolamento completo de dependências:

- **Localização:** `venv/`
- **Python:** 3.10+
- **Ativação:** `source venv/bin/activate`
- **Desativação:** `deactivate`

### Dependências de Produção
```
PySide6==6.10.1  # Interface gráfica
```

### Dependências de Desenvolvimento
```
pytest>=7.0.0           # Framework de testes
pytest-cov>=4.0.0       # Cobertura de código
pytest-html>=3.1.0      # Relatórios HTML
pytest-xdist>=3.0.0     # Execução paralela
pytest-mock>=3.10.0     # Mocking para testes
```

## ⚙️ Configurações e Scripts

### Scripts Automatizados
- **`run.sh`** - Execução da aplicação com ambiente
- **`t.sh`** - Suite completa de testes
- **`limpar_banco.py`** - Limpeza/reset do banco de dados

### Configurações
- **`pytest.ini`** - Configurações detalhadas de teste
- **`LegacyBJJ.spec`** - Build executável com PyInstaller
- **`PROTOCOLO_DESENVOLVIMENTO.md`** - Guia completo de desenvolvimento

## 🎯 Casos de Uso Principais

### 1. Cadastro de Novo Aluno Adulto
1. Acesso à aba "Cadastro"
2. Preenchimento de dados obrigatórios
3. Upload opcional de foto/certificado
4. Seleção de plano de pagamento
5. Geração automática de mensalidade

### 2. Cadastro de Kid com Responsável
1. Cadastro do responsável (se novo)
2. Vinculação automática ao responsável
3. Configuração de plano específico
4. Geração de mensalidade conforme regra

### 3. Controle Financeiro Mensal
1. Dashboard com métricas atualizadas
2. Visualização de mensalidades pendentes
3. Registro de pagamentos
4. Geração de relatórios PDF

### 4. Gestão de Presença Diária
1. Registro de entrada por aluno
2. Controle de horários de aula
3. Métricas de frequência automáticas
4. Relatórios de presença por período

## 🚧 Protocolo de Desenvolvimento

### Fluxo Obrigatório
1. **🛠 AJUSTE** - Implementar mudanças
2. **▶️ EXECUÇÃO** - `./run.sh` - Testar funcionalidade
3. **🧪 TESTE** - `./t.sh` - Verificar 93+ testes
4. **🔬 COBERTURA** - Validar/criar novos testes

### Padrões de Código
- **Modularização** clara por funcionalidade
- **Validação robusta** de dados de entrada
- **Tratamento de erro** consistente
- **Documentação** em docstrings
- **Testes** para toda nova funcionalidade

## 🎨 Personalização e Temas

### Estilos Customizáveis
- **`style.qss`** - Arquivo de estilos CSS
- **Cores personalizáveis** por academia
- **Layout responsivo** para diferentes telas
- **Componentes modulares** reutilizáveis

### Configurações Visuais
- Logo da academia personalizável
- Campos de formulário destacados
- Cards transparentes com bordas elegantes
- Botões com feedback visual

## 📱 Compatibilidade

### Sistemas Operacionais
- ✅ **Linux** (Ubuntu, Debian, CentOS)
- ✅ **macOS** (10.14+)
- ✅ **Windows** (10, 11)

### Requisitos Mínimos
- **Python:** 3.10 ou superior
- **RAM:** 4GB (recomendado 8GB)
- **Disco:** 500MB livres
- **Resolução:** 1024x768 (recomendado 1920x1080)

## 🤝 Contribuição e Suporte

### Para Desenvolvedores
1. Fork do repositório
2. Seguir `PROTOCOLO_DESENVOLVIMENTO.md`
3. Executar todos os testes antes do PR
4. Manter cobertura de código acima de 90%

### Suporte Técnico
- 📧 Suporte via issues do GitHub
- 📖 Documentação completa no código
- 🧪 Suite de testes para validação
- 📋 Protocolo de desenvolvimento detalhado

## 📈 Roadmap

### Próximas Funcionalidades
- [ ] **API REST** para integração externa
- [ ] **Sistema de backup** automático
- [ ] **Notificações** push por e-mail/SMS
- [ ] **Relatórios avançados** com gráficos
- [ ] **Integração biométrica** completa
- [ ] **App mobile** complementar

---

**Legacy BJJ** - Sistema completo para gestão profissional de academias de jiu-jitsu 🥋
