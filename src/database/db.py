import sqlite3

DB_NAME = "academia.db"


def connect():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS alunos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        telefone TEXT,
        valor_mensalidade REAL,
        dia_vencimento INTEGER,
        status TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS mensalidades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        aluno_id INTEGER,
        valor REAL,
        data_vencimento TEXT,
        data_pagamento TEXT,
        status TEXT,
        FOREIGN KEY(aluno_id) REFERENCES alunos(id)
    )
    """)

    conn.commit()
    conn.close()
