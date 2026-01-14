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
        cpf TEXT,
        data_nascimento TEXT,
        telefone TEXT,
        faixa TEXT,
        email TEXT,
        endereco TEXT,
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

    cur.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT UNIQUE,
        senha TEXT
    )
    """)

    cur.execute("SELECT COUNT(*) FROM usuarios")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO usuarios (usuario, senha) VALUES ('admin', '123')")

    conn.commit()
    conn.close()

