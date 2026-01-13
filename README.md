academia-jiu-jitsu/
│
├─ README.md
├─ .gitignore
├─ requirements.txt
│
├─ src/
│   ├─ main.py
│   │
│   ├─ database/
│   │   └─ db.py
│   │
│   ├─ models/
│   │   ├─ aluno.py
│   │   └─ mensalidade.py
│   │
│   ├─ services/
│   │   └─ financeiro_service.py
│   │
│   └─ ui/
│       ├─ alunos_tab.py
│       ├─ financeiro_tab.py
│       └─ alertas_tab.py
│
├─ assets/
│   └─ icons/
│
└─ build/
    └─ (ignorado pelo git)

# Sistema de Gestão - Academia de Jiu-Jitsu

Sistema desktop em Python para controle de alunos e mensalidades.

## Funcionalidades
- Cadastro de alunos
- Controle financeiro
- Alertas de vencimento

## Tecnologias
- Python 3.10+
- PySide6
- SQLite

## Como rodar
pip install -r requirements.txt
python src/main.py
