import sqlite3
from pathlib import Path

DB_PATH = Path("data.db")


def get_conn():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS alunos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        cpf TEXT,
        nascimento TEXT,
        telefone TEXT,
        email TEXT,
        endereco TEXT,
        faixa TEXT,
        graus TEXT,
        ativo INTEGER DEFAULT 1
    )
    """)

    cur.execute("SELECT COUNT(*) FROM usuarios")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO usuarios (username, password) VALUES ('admin','admin')")

    conn.commit()
    conn.close()


# ---------- LOGIN ----------
def validar_login(user, senha):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, username FROM usuarios WHERE username=? AND password=?",
        (user, senha),
    )
    res = cur.fetchone()
    conn.close()
    return res


# ---------- ALUNOS ----------
def inserir_aluno(dados):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO alunos
        (nome, cpf, nascimento, telefone, email, endereco, faixa, graus, ativo)
        VALUES (?,?,?,?,?,?,?,?,1)
    """, dados)
    conn.commit()
    conn.close()


def listar_alunos():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, nome, faixa, graus, telefone, ativo
        FROM alunos
        ORDER BY nome
    """)
    res = cur.fetchall()
    conn.close()
    return res


def inativar_aluno(aluno_id, ativo):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE alunos SET ativo=? WHERE id=?", (ativo, aluno_id))
    conn.commit()
    conn.close()


def excluir_aluno(aluno_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM alunos WHERE id=?", (aluno_id,))
    conn.commit()
    conn.close()
