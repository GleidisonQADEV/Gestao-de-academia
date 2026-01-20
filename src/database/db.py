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
    
    # Verificar e adicionar coluna biometria_data se não existir (para bancos existentes)
    try:
        cur.execute("SELECT biometria_data FROM alunos LIMIT 1")
    except sqlite3.OperationalError:
        # Coluna não existe, vamos adicioná-la
        cur.execute("ALTER TABLE alunos ADD COLUMN biometria_data TEXT")

    # ---- tabela mensalidades ----
    cur.execute("""
        CREATE TABLE IF NOT EXISTS mensalidades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aluno_id INTEGER NOT NULL,
            valor REAL NOT NULL,
            data_vencimento DATE NOT NULL,
            data_pagamento DATE,
            status TEXT DEFAULT 'PENDENTE',
            observacoes TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (aluno_id) REFERENCES alunos (id)
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


# ---------------- FINANCEIRO ----------------

def listar_mensalidades(status=None):
    """Lista mensalidades com informações do aluno"""
    conn = get_conn()
    cur = conn.cursor()
    
    query = """
        SELECT 
            m.id, 
            a.nome, 
            m.valor, 
            m.data_vencimento, 
            m.data_pagamento, 
            m.status,
            m.observacoes,
            a.foto_path,
            a.plano
        FROM mensalidades m
        JOIN alunos a ON m.aluno_id = a.id
        WHERE a.ativo = 1
    """
    
    if status:
        query += " AND m.status = ?"
        cur.execute(query + " ORDER BY m.data_vencimento DESC", (status,))
    else:
        cur.execute(query + " ORDER BY m.data_vencimento DESC")
    
    dados = cur.fetchall()
    conn.close()
    return dados


def criar_mensalidade(aluno_id, valor, data_vencimento, observacoes=None):
    """Cria uma nova mensalidade"""
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO mensalidades (aluno_id, valor, data_vencimento, observacoes)
        VALUES (?, ?, ?, ?)
    """, (aluno_id, valor, data_vencimento, observacoes))
    
    mensalidade_id = cur.lastrowid
    conn.commit()
    conn.close()
    return mensalidade_id


def marcar_mensalidade_paga(mensalidade_id, data_pagamento, observacoes=None):
    """Marca uma mensalidade como paga"""
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute("""
        UPDATE mensalidades 
        SET status = 'PAGO', data_pagamento = ?, observacoes = ?
        WHERE id = ?
    """, (data_pagamento, observacoes, mensalidade_id))
    
    conn.commit()
    conn.close()


def obter_mensalidades_pendentes():
    """Obtém mensalidades pendentes em atraso"""
    from datetime import date
    hoje = date.today().isoformat()
    
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            m.id, 
            a.nome, 
            m.valor, 
            m.data_vencimento,
            julianday('now') - julianday(m.data_vencimento) as dias_atraso
        FROM mensalidades m
        JOIN alunos a ON m.aluno_id = a.id
        WHERE m.status = 'PENDENTE' 
        AND m.data_vencimento < ?
        AND a.ativo = 1
        ORDER BY m.data_vencimento
    """, (hoje,))
    
    dados = cur.fetchall()
    conn.close()
    return dados


# FUNÇÃO DESABILITADA - Sistema automático implementado na UI
# def gerar_mensalidades_automaticas():
#     """Gera mensalidades automáticas para o mês atual"""
#     from datetime import date, datetime
#     hoje = date.today()
#     mes_atual = hoje.month
#     ano_atual = hoje.year
#     
#     conn = get_conn()
#     cur = conn.cursor()
#     
#     # Buscar alunos ativos com planos definidos
#     cur.execute("""
#         SELECT id, nome, plano
#         FROM alunos 
#         WHERE ativo = 1 AND plano IS NOT NULL AND plano != ''
#     """)
#     alunos = cur.fetchall()
#     
#     mensalidades_criadas = 0
#     
#     for aluno_id, nome, plano in alunos:
#         # Verificar se já existe mensalidade para este mês
#         cur.execute("""
#             SELECT id FROM mensalidades 
#             WHERE aluno_id = ? 
#             AND strftime('%m', data_vencimento) = ? 
#             AND strftime('%Y', data_vencimento) = ?
#         """, (aluno_id, f"{mes_atual:02d}", str(ano_atual)))
#         
#         if cur.fetchone():
#             continue  # Já existe mensalidade para este mês
#         
#         # Determinar valor baseado no plano
#         valor = 180.0  # Valor padrão
#         if "musculação" in plano.lower():
#             valor = 150.0
#         elif "kids" in plano.lower():
#             valor = 120.0
#         elif "premium" in plano.lower():
#             valor = 300.0
#         
#         # Data de vencimento (dia 10 do mês)
#         try:
#             data_vencimento = date(ano_atual, mes_atual, 10)
#         except ValueError:
#             data_vencimento = date(ano_atual, mes_atual, 28)  # Caso não seja possível
#         
#         # Criar mensalidade
#         cur.execute("""
#             INSERT INTO mensalidades (aluno_id, valor, data_vencimento, observacoes)
#             VALUES (?, ?, ?, ?)
#         """, (aluno_id, valor, data_vencimento.isoformat(), f"Mensalidade automática - {plano}"))
#         
#         mensalidades_criadas += 1
#     
#     conn.commit()
#     conn.close()
#     return mensalidades_criadas

def gerar_mensalidades_automaticas():
    """FUNÇÃO DESABILITADA - usar sistema automático da UI"""
    return 0
