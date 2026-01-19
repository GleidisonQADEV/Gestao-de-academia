import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "legacy_bjj.db")


# ---------------- CONEXÃO ----------------

def get_conn():
    return sqlite3.connect(DB_PATH)


# ---------------- INIT KIDS ----------------

def init_kids_db():
    conn = get_conn()
    cur = conn.cursor()

    # Verificar se a tabela existe e se tem a estrutura antiga
    cur.execute("PRAGMA table_info(kids)")
    columns = cur.fetchall()
    
    # Se a tabela existe, verificar se CPF é NOT NULL
    cpf_is_not_null = False
    if columns:
        for column in columns:
            if column[1] == 'cpf' and column[3] == 1:  # column[3] indica NOT NULL
                cpf_is_not_null = True
                break
    
    # Se CPF é NOT NULL, precisamos recriar a tabela
    if cpf_is_not_null:
        print("Migrando tabela kids para permitir CPF opcional...")
        
        # Criar tabela temporária com nova estrutura
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

                ativo INTEGER DEFAULT 1,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Copiar dados existentes (apenas os que têm CPF)
        cur.execute("""
            INSERT INTO kids_new 
            SELECT * FROM kids WHERE cpf IS NOT NULL AND cpf != ''
        """)
        
        # Remover tabela antiga e renomear
        cur.execute("DROP TABLE kids")
        cur.execute("ALTER TABLE kids_new RENAME TO kids")
        
        print("Migração concluída!")
    else:
        # Criar tabela normalmente se não existe
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

                ativo INTEGER DEFAULT 1,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

    conn.commit()
    conn.close()


# ---------------- VALIDAÇÃO ----------------

def cpf_kid_existe(cpf):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM kids WHERE cpf=?", (cpf,))
    r = cur.fetchone()
    conn.close()
    return r is not None


# ---------------- INSERÇÃO ----------------

def inserir_kid(
    nome, cpf, resp_nome, resp_cpf, email, telefone, cep, endereco, data_nasc,
    faixa, grau, peso, altura, plano, foto_path, certificado_path
):
    conn = get_conn()
    cur = conn.cursor()
    
    try:
        # Se CPF não foi fornecido, criar identificador baseado no responsável
        if not cpf:
            # Usar primeiros 6 dígitos do CPF do responsável + timestamp simples para unicidade
            import time
            timestamp_suffix = str(int(time.time()))[-4:]
            cpf = f"KID{resp_cpf[:6]}{timestamp_suffix}"
        
        cur.execute("""
            INSERT INTO kids (
                nome, cpf, resp_nome, resp_cpf, email, telefone, cep, endereco,
                data_nascimento, faixa, grau, peso, altura, plano,
                foto_path, certificado_path
            )
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            nome, cpf, resp_nome, resp_cpf, email, telefone, cep, endereco,
            data_nasc, faixa, grau, peso, altura, plano, foto_path, certificado_path
        ))

        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
