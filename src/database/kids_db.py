import sqlite3
import os
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "legacy_bjj.db")


# ---------------- CONEXÃO ----------------

def get_conn():
    return sqlite3.connect(DB_PATH)


# ---------------- INIT KIDS ----------------

def init_kids_db():
    conn = get_conn()
    cur = conn.cursor()

    # Verificar estrutura da tabela
    cur.execute("PRAGMA table_info(kids)")
    columns = cur.fetchall()

    cpf_is_not_null = False
    if columns:
        for column in columns:
            if column[1] == 'cpf' and column[3] == 1:  # NOT NULL
                cpf_is_not_null = True
                break

    # Migrar se necessário
    if cpf_is_not_null:
        print("Migrando tabela kids para permitir CPF opcional...")

        cur.execute("""
            CREATE TABLE kids_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cpf TEXT UNIQUE,

                resp_nome TEXT NOT NULL,
                resp_cpf TEXT NOT NULL,

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

        cur.execute("""
            INSERT INTO kids_new 
            SELECT * FROM kids WHERE cpf IS NOT NULL AND cpf != ''
        """)

        cur.execute("DROP TABLE kids")
        cur.execute("ALTER TABLE kids_new RENAME TO kids")

        print("Migração kids concluída.")

    else:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS kids (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cpf TEXT UNIQUE,

                resp_nome TEXT NOT NULL,
                resp_cpf TEXT NOT NULL,

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


# ---------------- LISTAGEM ----------------

def listar_kids():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            id,                -- 0
            nome,              -- 1
            cpf,               -- 2
            resp_nome,         -- 3
            resp_cpf,          -- 4
            email,             -- 5
            telefone,          -- 6
            cep,               -- 7
            endereco,          -- 8
            data_nascimento,   -- 9
            faixa,             --10
            grau,              --11
            peso,              --12
            altura,            --13
            plano,             --14
            foto_path,         --15
            certificado_path,  --16
            ativo,             --17
            criado_em          --18
        FROM kids
        ORDER BY nome
    """)

    rows = cur.fetchall()
    conn.close()
    return rows


# ---------------- VALIDAÇÃO ----------------

def cpf_kid_existe(cpf, excluir_id=None):
    """Verifica se CPF já existe, opcionalmente excluindo um ID específico (para edição)"""
    if not cpf:
        return False
    
    conn = get_conn()
    cur = conn.cursor()
    
    if excluir_id:
        cur.execute("SELECT 1 FROM kids WHERE cpf=? AND id!=?", (cpf, excluir_id))
    else:
        cur.execute("SELECT 1 FROM kids WHERE cpf=?", (cpf,))
    
    r = cur.fetchone()
    conn.close()
    return r is not None


# ---------------- ATUALIZAÇÃO ----------------

def atualizar_kid(
    kid_id, nome, cpf, resp_nome, resp_cpf, email, telefone, cep, endereco, data_nasc,
    faixa, grau, peso, altura, plano, foto_path, certificado_path, biometria_data=None
):
    """Atualiza todos os dados de uma criança"""
    conn = get_conn()
    cur = conn.cursor()
    
    try:
        # Se não há CPF, gerar um automático
        if not cpf:
            timestamp_suffix = str(int(time.time()))[-4:]
            cpf = f"KID{resp_cpf[:6]}{timestamp_suffix}"
        
        cur.execute("""
            UPDATE kids SET 
                nome=?, cpf=?, resp_nome=?, resp_cpf=?, email=?, telefone=?, 
                cep=?, endereco=?, data_nascimento=?,
                faixa=?, grau=?, peso=?, altura=?, plano=?,
                foto_path=?, certificado_path=?, biometria_data=?
            WHERE id=?
        """, (
            nome, cpf, resp_nome, resp_cpf, email, telefone, cep, endereco,
            data_nasc, faixa, grau, peso, altura, plano, foto_path, certificado_path, biometria_data,
            kid_id
        ))
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


# ---------------- STATUS ----------------

def inativar_kid(kid_id, ativo):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE kids SET ativo=? WHERE id=?", (ativo, kid_id))
    conn.commit()
    conn.close()


# ---------------- EXCLUSÃO ----------------

def excluir_kid(kid_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM kids WHERE id=?", (kid_id,))
    conn.commit()
    conn.close()


# ---------------- INSERÇÃO ----------------

def inserir_kid(
    nome, cpf, resp_nome, resp_cpf, email, telefone, cep, endereco, data_nasc,
    faixa, grau, peso, altura, plano, foto_path, certificado_path, biometria_data=None
):
    conn = get_conn()
    cur = conn.cursor()

    try:
        if not cpf:
            timestamp_suffix = str(int(time.time()))[-4:]
            cpf = f"KID{resp_cpf[:6]}{timestamp_suffix}"

        cur.execute("""
            INSERT INTO kids (
                nome, cpf, resp_nome, resp_cpf, email, telefone, cep, endereco,
                data_nascimento, faixa, grau, peso, altura, plano,
                foto_path, certificado_path, biometria_data
            )
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            nome, cpf, resp_nome, resp_cpf, email, telefone, cep, endereco,
            data_nasc, faixa, grau, peso, altura, plano, foto_path, certificado_path, biometria_data
        ))

        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
