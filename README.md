# Sistema de Gestão de Academia - Legacy BJJ

Sistema desktop em Python para controle de alunos e mensalidades.

## Como executar a aplicação

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

## Credenciais de Acesso

- **Usuário:** admin
- **Senha:** senha

## Funcionalidades

### Pesquisa de Alunos
- **Pesquisa específica:** Digite o nome, CPF ou responsável do aluno
- **Listar todos:** Digite "todos" para ver todos os alunos cadastrados em ordem alfabética
- Os resultados aparecem em cards lado a lado (máximo 2 cards por busca específica)
- Para "todos", os alunos são mostrados em um layout de grid com scroll

### Cards de Alunos
- Design transparente com campos individuais em branco
- Exibição de foto, dados pessoais, faixa, plano e status
- Botões de ação: Editar, Ativar/Inativar, Excluir

### Cadastro
- Cadastro de alunos adultos e kids
- Validação de campos obrigatórios
- Upload de fotos
- Auto-refresh após cadastro

## Tecnologias
- Python 3.10+
- PySide6 (Interface gráfica)
- SQLite (Banco de dados)

## Ambiente Virtual

O projeto utiliza um ambiente virtual Python (venv) para isolamento das dependências:

- **Localização:** `venv/`
- **Dependências:** PySide6
- **Ativação:** `source venv/bin/activate`
- **Desativação:** `deactivate`

## Estrutura do Projeto

```
src/
├── main.py                 # Arquivo principal
├── database/
│   ├── db.py              # Banco de dados principal
│   └── kids_db.py         # Banco de dados kids
├── ui/
│   ├── alunos_tab.py      # Aba de visualização de alunos
│   ├── cadastro_aluno_tab.py # Aba de cadastro
│   ├── login_window.py    # Tela de login
│   └── ...
└── assets/
    └── logo.png           # Logo da academia
```
