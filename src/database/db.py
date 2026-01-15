import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "legacy_bjj.db")


# ---------------------------
def get_conn():
    return sqlite3.connect(DB_PATH)


# ---------------------------
def init_db():
    conn = get_conn()
    cur = conn.cursor()

    # USUÁRIOS (login)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT UNIQUE,
        senha TEXT
    )
    """)

    # ALUNOS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS alunos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        cpf TEXT,
        email TEXT,
        telefone TEXT,
        cep TEXT,
        endereco TEXT,
        nascimento TEXT,
        faixa TEXT,
        grau TEXT,
        foto_path TEXT,
        certificado_path TEXT,
        ativo INTEGER DEFAULT 1
    )
    """)

    # usuário padrão
    cur.execute("SELECT COUNT(*) FROM usuarios")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO usuarios (usuario, senha) VALUES (?, ?)", ("admin", "admin"))

    conn.commit()
    conn.close()


# ---------------------------
def validar_login(usuario, senha):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM usuarios WHERE usuario=? AND senha=?", (usuario, senha))
    res = cur.fetchone()
    conn.close()
    return res


# ---------------------------
def inserir_aluno(nome, cpf, email, telefone, cep, endereco, nascimento,
                  faixa, grau, foto_path, certificado_path):

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO alunos (
            nome, cpf, email, telefone, cep, endereco, nascimento,
            faixa, grau, foto_path, certificado_path, ativo
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
    """, (
        nome, cpf, email, telefone, cep, endereco, nascimento,
        faixa, grau, foto_path, certificado_path
    ))

    conn.commit()
    conn.close()


# ---------------------------
def listar_alunos(ativos_only=True):
    conn = get_conn()
    cur = conn.cursor()

    if ativos_only:
        cur.execute("SELECT * FROM alunos WHERE ativo=1 ORDER BY nome")
    else:
        cur.execute("SELECT * FROM alunos ORDER BY nome")

    rows = cur.fetchall()
    conn.close()
    return rows


# ---------------------------
def inativar_aluno(aluno_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE alunos SET ativo=0 WHERE id=?", (aluno_id,))
    conn.commit()
    conn.close()


# ---------------------------
def ativar_aluno(aluno_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE alunos SET ativo=1 WHERE id=?", (aluno_id,))
    conn.commit()
    conn.close()


# ---------------------------
def excluir_aluno(aluno_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM alunos WHERE id=?", (aluno_id,))
    conn.commit()
    conn.close()
