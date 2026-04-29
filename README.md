# Sistema de Gestão de Academia - Legacy BJJ

Sistema desktop completo em Python para gestão integrada de academia de jiu-jitsu: alunos adultos e kids, mensalidades, controle de presença e relatórios financeiros.

---

## Download e Instalação

### Instaladores prontos (recomendado)

Acesse a página de [**Releases**](https://github.com/GleidisonQADEV/Gestao-de-academia/releases/latest) do repositório e baixe o instalador para o seu sistema:

| Sistema | Arquivo | Como instalar |
|---------|---------|---------------|
| **macOS** | `LegacyBJJ-X.X.X-mac.dmg` | Abra o `.dmg`, arraste o app para a pasta Aplicativos |
| **Windows** | `LegacyBJJ-X.X.X-windows-setup.exe` | Execute o `.exe` e siga o assistente de instalação |

> O aplicativo verifica atualizações automaticamente na inicialização. Quando uma nova versão for lançada, um botão de atualização aparece na barra lateral.

---

## Execução pelo código-fonte

### Pré-requisitos

- Python 3.10 ou superior
- `venv` disponível

### Configuração

```bash
# Clonar o repositório
git clone https://github.com/GleidisonQADEV/Gestao-de-academia.git
cd Gestao-de-academia

# Criar e ativar ambiente virtual
python3 -m venv venv
source venv/bin/activate          # macOS/Linux
# venv\Scripts\activate           # Windows

# Instalar dependências
pip install -r requirements.txt
```

### Executar

```bash
./run.sh
```

Ou manualmente:

```bash
source venv/bin/activate
python3 src/main.py
```

### Credenciais padrão

| Campo | Valor |
|-------|-------|
| Usuário | `admin` |
| Senha | `senha` |

---

## Funcionalidades

### Gestão de Alunos
- Cadastro completo de adultos e kids (5–13 anos)
- Sistema de responsáveis e dependentes com vinculação automática
- Pesquisa por nome, CPF ou responsável
- Controle de status (ativo/inativo)
- Upload de fotos e certificados

### Sistema Financeiro
- Mensalidades organizadas por mês com abas navegáveis
- Geração automática para responsáveis ativos no início de cada mês
- Status de pagamento: Pendente, Pago, Atrasado
- Filtro por status e registro de pagamento direto no card
- Edição de mensalidades individuais
- Dependentes não geram mensalidade própria — cobertos pelo plano do responsável

### Dashboard
- Métricas de alunos ativos com lista scrollável por faixa e plano
- Indicadores financeiros em tempo real
- Alertas de inadimplência e vencimentos

### Controle de Presença
- Registro de entrada e saída por horário de aula
- Métricas de frequência considerando apenas dias letivos
- Histórico por aluno e relatórios por período

### Gestão de Planos
- Planos pré-configurados (Adulto, Kids, Família)
- Planos personalizados com valores livres
- Planos especiais: Bolsista, Vinculado ao responsável

### Temas (V0 / V1)
- **V1** (padrão): dark theme moderno, sidebar com navegação
- **V0**: versão legada com marca d'água — acessível via botão no sidebar
- Alternância reinicia o app preservando o banco de dados

### Atualizações automáticas
- Verificação de nova versão via GitHub Releases na inicialização (3 s de delay)
- Download em background com barra de progresso
- Botão de atualização visível no sidebar quando há nova versão disponível
- Abre o instalador correspondente ao sistema operacional

---

## Estrutura do projeto

```
Gestao-de-academia/
├── run.sh                          # Inicia a aplicação
├── t.sh                            # Executa suite de testes
├── LegacyBJJ.spec                  # Configuração PyInstaller
├── PROTOCOLO_DESENVOLVIMENTO.md    # Guia de desenvolvimento
├── requirements.txt
├── requirements-test.txt
│
├── src/
│   ├── main.py                     # Janela principal + auto-updater
│   ├── version.py                  # APP_VERSION e GITHUB_REPO
│   │
│   ├── assets/
│   │   ├── logo.png
│   │   ├── icon.icns               # Ícone macOS
│   │   └── icon.ico                # Ícone Windows
│   │
│   ├── database/
│   │   ├── db.py                   # Banco principal (alunos adultos, mensalidades)
│   │   └── kids_db.py              # Banco kids
│   │
│   ├── ui/
│   │   ├── main.py / login_window.py
│   │   ├── dashboard_tab.py        # Dashboard com card de alunos scrollável
│   │   ├── alunos_tab.py           # Listagem com filtros e faixas
│   │   ├── cadastro_aluno_tab.py   # Cadastro adultos e kids
│   │   ├── financeiro_tab.py       # Gestão financeira por mês
│   │   ├── alertas_tab.py          # Alertas de inadimplência
│   │   ├── config_tab.py           # Configurações e planos
│   │   ├── aluno_profile.py        # Perfil detalhado do aluno
│   │   ├── updater.py              # UpdateChecker e Downloader (QThread)
│   │   ├── app_dialog.py           # Diálogos padronizados
│   │   └── *_v0.py                 # Versões legadas (tema V0)
│   │
│   └── utils/
│       ├── pdf_report.py           # Relatórios PDF (requer reportlab)
│       └── vincular_utils.py       # Vinculação responsável/dependente
│
├── scripts/
│   ├── build_mac.sh                # Build local macOS → .dmg
│   └── convert_icons.py            # logo.png → .icns + .ico
│
├── installer/
│   └── setup.iss                   # Script Inno Setup (Windows)
│
├── .github/workflows/
│   └── build-release.yml           # CI/CD: build Mac + Windows em tag v*.*.*
│
└── tests/
    ├── conftest.py
    ├── unit/                       # Testes unitários
    └── integration/                # Testes de integração
```

---

## Banco de dados

Arquivo SQLite local em `src/database/legacy_bjj.db`.

| Tabela | Descrição |
|--------|-----------|
| `users` | Autenticação |
| `alunos` | Alunos adultos (`responsavel_id` para dependentes) |
| `kids` | Alunos infantis |
| `mensalidades` | Controle financeiro (`aluno_id` negativo = kid) |
| `planos` | Planos de pagamento |
| `registros_presenca` | Frequência |
| `configuracoes` | Chaves internas (ex: controle de reset mensal) |

---

## Testes

```bash
# Suite completa
./t.sh

# Sem os testes que causam segfault (Qt sem QApplication)
python3 -m pytest tests/ --ignore=tests/unit/test_ui_main_window.py \
                         --ignore=tests/unit/test_dashboard_ui.py -q

# Arquivo específico
python3 -m pytest tests/unit/test_mensalidades_dependentes.py -v
```

**Estado atual:** 100 testes passando, 3 skipped (reportlab opcional).

---

## Build e release

### Gerar instalador macOS localmente

```bash
bash scripts/build_mac.sh
# Gera: dist/LegacyBJJ-{versão}-mac.dmg
```

Requer PyInstaller e opcionalmente `create-dmg` (`brew install create-dmg`).

### Gerar instalador Windows localmente

```bash
source venv/bin/activate
pyinstaller LegacyBJJ.spec --noconfirm --clean
# Depois abrir installer/setup.iss no Inno Setup Compiler
```

### Release automático via GitHub Actions

Crie e envie uma tag no formato `vX.Y.Z`:

```bash
git tag v1.0.1
git push origin v1.0.1
```

O workflow `.github/workflows/build-release.yml` compila automaticamente para macOS e Windows e publica os arquivos na página de Releases.

---

## Tecnologias

| Categoria | Tecnologia |
|-----------|------------|
| Linguagem | Python 3.10+ |
| Interface | PySide6 |
| Banco de dados | SQLite |
| Build | PyInstaller 6+ |
| Instalador Windows | Inno Setup |
| Testes | pytest, pytest-cov, pytest-html |
| CI/CD | GitHub Actions |

---

## Requisitos mínimos

| Item | Requisito |
|------|-----------|
| Sistema operacional | macOS 12+, Windows 10/11 |
| RAM | 4 GB (8 GB recomendado) |
| Disco | 500 MB livres |
| Resolução | 1024×768 (1920×1080 recomendado) |

---

## Desenvolvimento

Consulte o [PROTOCOLO_DESENVOLVIMENTO.md](PROTOCOLO_DESENVOLVIMENTO.md) para o fluxo obrigatório:
ajuste → execução → testes → cobertura → limpeza → commit → push.

---

**Legacy BJJ** — gestão profissional de academias de jiu-jitsu
