import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "legacy_bjj.db")


# ---------------- CONEXÃO ----------------

def get_conn():
    return sqlite3.connect(DB_PATH)


# ---------------- INIT ----------------

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    # ---- usuários (login) ----
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # usuário padrão
    cur.execute("SELECT 1 FROM users WHERE username='admin'")
    if not cur.fetchone():
        cur.execute(
            "INSERT INTO users (username, password) VALUES (?,?)",
            ("admin", "senha")
        )

    # ---- alunos adultos ----
    cur.execute("""
        CREATE TABLE IF NOT EXISTS alunos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cpf TEXT NOT NULL UNIQUE,
            email TEXT,
            telefone TEXT NOT NULL,
            cep TEXT NOT NULL,
            endereco TEXT NOT NULL,
            data_nascimento TEXT NOT NULL,

            faixa TEXT,
            grau TEXT,
            peso TEXT,
            altura TEXT,

            plano TEXT,

            foto_path TEXT,
            certificado_path TEXT,
            biometria_data TEXT,

            ativo INTEGER DEFAULT 1,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


# ---------------- LOGIN ----------------

def validar_login(username, password):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, password)
    )
    user = cur.fetchone()
    conn.close()
    return user


# ---------------- ALUNOS ----------------

def inserir_aluno(
    nome, cpf, email, telefone, cep, endereco, data_nasc,
    faixa, grau, peso, altura, plano,
    foto_path, certificado_path, biometria_data=None
):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO alunos (
            nome, cpf, email, telefone, cep, endereco, data_nascimento,
            faixa, grau, peso, altura, plano,
            foto_path, certificado_path, biometria_data
        )
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        nome, cpf, email, telefone, cep, endereco, data_nasc,
        faixa, grau, peso, altura, plano,
        foto_path, certificado_path, biometria_data
    ))

    conn.commit()
    conn.close()


def listar_alunos():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM alunos WHERE ativo=1 ORDER BY nome")
    rows = cur.fetchall()
    conn.close()
    return rows


def listar_todos_alunos():
    """Lista todos os alunos (ativos e inativos)"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM alunos ORDER BY nome")
    rows = cur.fetchall()
    conn.close()
    return rows


def excluir_aluno(aluno_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM alunos WHERE id=?", (aluno_id,))
    conn.commit()
    conn.close()


def inativar_aluno(aluno_id, novo_status=0):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE alunos SET ativo=? WHERE id=?", (novo_status, aluno_id))
    conn.commit()
    conn.close()


def atualizar_aluno(
    aluno_id, nome, cpf, email, telefone, cep, endereco, data_nasc,
    faixa, grau, peso, altura, plano, foto_path, certificado_path, biometria_data=None
):
    """Atualiza todos os dados de um aluno"""
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute("""
        UPDATE alunos SET 
            nome=?, cpf=?, email=?, telefone=?, cep=?, endereco=?, data_nascimento=?,
            faixa=?, grau=?, peso=?, altura=?, plano=?,
            foto_path=?, certificado_path=?, biometria_data=?
        WHERE id=?
    """, (
        nome, cpf, email, telefone, cep, endereco, data_nasc,
        faixa, grau, peso, altura, plano,
        foto_path, certificado_path, biometria_data, aluno_id
    ))
    
    conn.commit()
    conn.close()


# ---------------- VALIDAÇÕES ----------------

def cpf_existe(cpf, excluir_id=None):
    """Verifica se CPF já existe, opcionalmente excluindo um ID específico (para edição)"""
    conn = get_conn()
    cur = conn.cursor()
    
    if excluir_id:
        cur.execute("SELECT 1 FROM alunos WHERE cpf=? AND id!=?", (cpf, excluir_id))
    else:
        cur.execute("SELECT 1 FROM alunos WHERE cpf=?", (cpf,))
    
    r = cur.fetchone()
    conn.close()
    return r is not None


def email_existe(email, excluir_id=None):
    """Verifica se email já existe, opcionalmente excluindo um ID específico (para edição)"""
    if not email:
        return False
    
    conn = get_conn()
    cur = conn.cursor()
    
    if excluir_id:
        cur.execute("SELECT 1 FROM alunos WHERE email=? AND id!=?", (email, excluir_id))
    else:
        cur.execute("SELECT 1 FROM alunos WHERE email=?", (email,))
    
    r = cur.fetchone()
    conn.close()
    return r is not None
