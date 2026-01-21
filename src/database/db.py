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
        
    # Verificar e adicionar coluna responsavel_id se não existir (para vínculos de dependentes)
    try:
        cur.execute("SELECT responsavel_id FROM alunos LIMIT 1")
    except sqlite3.OperationalError:
        # Coluna não existe, vamos adicioná-la
        cur.execute("ALTER TABLE alunos ADD COLUMN responsavel_id INTEGER")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_alunos_responsavel_id ON alunos(responsavel_id)")

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
    
    # ---- tabela planos ----
    cur.execute("""
        CREATE TABLE IF NOT EXISTS planos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            valor REAL NOT NULL,
            ativo INTEGER DEFAULT 1,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Inserir planos padrão se a tabela estiver vazia
    cur.execute("SELECT COUNT(*) FROM planos")
    if cur.fetchone()[0] == 0:
        planos_padrao = [
            ("Adulto", 180.0),
            ("Kids (5-13)", 150.0),
            ("Família: 2 adultos", 320.0),
            ("Família: 1 adulto + 1 kids", 300.0),
            ("Família: 2 adultos + 1 kids", 450.0),
            ("Família: 1 adulto + 2 kids", 430.0),
            ("Família: 1 adulto + 3 kids", 500.0),
            ("Plano Bolsista (Patrocinado)", 0.0)
        ]
        cur.executemany("INSERT INTO planos (nome, valor) VALUES (?, ?)", planos_padrao)

    # ---- tabela kids ----
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
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            responsavel_cpf TEXT
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

    # Obter ID do aluno inserido
    aluno_id = cur.lastrowid

    # Gerar mensalidade automaticamente se o plano não for gratuito
    if plano and "R$0" not in plano and "Bolsista" not in plano and "Vinculado ao responsável" not in plano:
        from datetime import date, datetime
        
        # Extrair valor do plano
        try:
            import re
            match = re.search(r'R\$(\d+(?:\.\d{2})?)', plano)
            if match:
                valor = float(match.group(1))
                
                # Data de vencimento: dia 10 do mês atual
                hoje = date.today()
                data_vencimento = date(hoje.year, hoje.month, 10)
                
                # Se já passou do dia 10, vencimento é no próximo mês
                if hoje.day > 10:
                    if hoje.month == 12:
                        data_vencimento = date(hoje.year + 1, 1, 10)
                    else:
                        data_vencimento = date(hoje.year, hoje.month + 1, 10)
                
                # Inserir mensalidade
                cur.execute("""
                    INSERT INTO mensalidades (aluno_id, valor, data_vencimento, status, observacoes)
                    VALUES (?, ?, ?, 'PENDENTE', 'Mensalidade gerada automaticamente no cadastro')
                """, (aluno_id, valor, data_vencimento))
        except:
            pass  # Se não conseguir extrair valor, apenas pula

    conn.commit()
    conn.close()
    
    return aluno_id


def listar_alunos():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM alunos WHERE ativo=1 ORDER BY nome")
    rows = cur.fetchall()
    conn.close()
    return rows


def listar_todos_alunos():
    """Lista todos os alunos (ativos e inativos) com informações de responsáveis e dependentes"""
    conn = get_conn()
    cur = conn.cursor()
    
    # Query simples primeiro para pegar todos os alunos com responsáveis
    cur.execute("""
        SELECT 
            a.*,
            r.nome as responsavel_nome,
            r.cpf as responsavel_cpf
        FROM alunos a
        LEFT JOIN alunos r ON a.responsavel_id = r.id
        ORDER BY a.nome
    """)
    
    alunos = cur.fetchall()
    
    # Agora pegar os dependentes para cada aluno
    resultado_final = []
    for aluno in alunos:
        aluno_id = aluno[0]  # ID está na primeira posição
        
        # Buscar dependentes deste aluno
        cur.execute("""
            SELECT nome FROM alunos 
            WHERE responsavel_id = ? AND ativo = 1
        """, (aluno_id,))
        dependentes = cur.fetchall()
        
        # Criar tupla estendida com informações de dependentes
        dependentes_nomes = ', '.join([dep[0] for dep in dependentes]) if dependentes else None
        total_dependentes = len(dependentes)
        
        # Adicionar as colunas extras
        aluno_completo = aluno + (dependentes_nomes, total_dependentes)
        resultado_final.append(aluno_completo)
    
    conn.close()
    return resultado_final


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
    """Lista mensalidades com informações do aluno (adultos e kids)"""
    conn = get_conn()
    cur = conn.cursor()
    
    # Query que une mensalidades com alunos adultos E kids
    query = """
        SELECT 
            m.id, 
            COALESCE(a.nome, k.nome) as nome,
            m.valor, 
            m.data_vencimento, 
            m.data_pagamento, 
            m.status,
            m.observacoes,
            COALESCE(a.foto_path, k.foto_path) as foto_path,
            COALESCE(a.plano, k.plano) as plano,
            CASE 
                WHEN a.id IS NOT NULL THEN 'adulto'
                WHEN k.id IS NOT NULL THEN 'kid'
                ELSE 'unknown'
            END as tipo_aluno
        FROM mensalidades m
        LEFT JOIN alunos a ON m.aluno_id = a.id AND a.ativo = 1 AND a.responsavel_id IS NULL
        LEFT JOIN kids k ON m.aluno_id = -k.id AND k.ativo = 1
        WHERE (a.id IS NOT NULL OR k.id IS NOT NULL)
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


def gerar_mensalidades_automaticas():
    """Gera mensalidades para alunos que não possuem mensalidades no mês atual"""
    from datetime import date
    import re
    
    conn = get_conn()
    cur = conn.cursor()
    
    hoje = date.today()
    data_vencimento = date(hoje.year, hoje.month, 10)
    if hoje.day > 10:
        if hoje.month == 12:
            data_vencimento = date(hoje.year + 1, 1, 10)
        else:
            data_vencimento = date(hoje.year, hoje.month + 1, 10)
    
    mensalidades_criadas = 0
    
    # Processar alunos adultos (excluir dependentes vinculados a responsáveis)
    cur.execute("SELECT id, nome, plano FROM alunos WHERE ativo = 1 AND responsavel_id IS NULL")
    alunos = cur.fetchall()
    
    for aluno_id, nome, plano in alunos:
        # Verificar se já tem mensalidade no mês atual
        cur.execute("""
            SELECT COUNT(*) FROM mensalidades 
            WHERE aluno_id = ? AND strftime('%Y-%m', data_vencimento) = ?
        """, (aluno_id, data_vencimento.strftime('%Y-%m')))
        
        if cur.fetchone()[0] == 0:  # Não tem mensalidade no mês
            # Extrair valor do plano
            if plano and "R$0" not in plano and "Bolsista" not in plano:
                try:
                    match = re.search(r'R\$(\d+(?:\.\d{2})?)', plano)
                    if match:
                        valor = float(match.group(1))
                        cur.execute("""
                            INSERT INTO mensalidades (aluno_id, valor, data_vencimento, status, observacoes)
                            VALUES (?, ?, ?, 'PENDENTE', 'Mensalidade gerada automaticamente')
                        """, (aluno_id, valor, data_vencimento))
                        mensalidades_criadas += 1
                        print(f"Mensalidade criada para {nome}: R${valor}")
                except:
                    pass
    
    # Processar kids
    cur.execute("SELECT id, nome, plano FROM kids WHERE ativo = 1")
    kids = cur.fetchall()
    
    for kid_id, nome, plano in kids:
        # Verificar se já tem mensalidade no mês atual
        cur.execute("""
            SELECT COUNT(*) FROM mensalidades 
            WHERE aluno_id = ? AND strftime('%Y-%m', data_vencimento) = ?
        """, (-kid_id, data_vencimento.strftime('%Y-%m')))
        
        if cur.fetchone()[0] == 0:  # Não tem mensalidade no mês
            # Extrair valor do plano
            if plano and "R$0" not in plano and "Bolsista" not in plano and "Vinculado ao responsável" not in plano:
                try:
                    match = re.search(r'R\$(\d+(?:\.\d{2})?)', plano)
                    if match:
                        valor = float(match.group(1))
                        cur.execute("""
                            INSERT INTO mensalidades (aluno_id, valor, data_vencimento, status, observacoes)
                            VALUES (?, ?, ?, 'PENDENTE', 'Mensalidade gerada automaticamente (Kids)')
                        """, (-kid_id, valor, data_vencimento))
                        mensalidades_criadas += 1
                        print(f"Mensalidade criada para {nome} (Kids): R${valor}")
                except:
                    pass
    
    conn.commit()
    conn.close()
    
    print(f"Total de mensalidades criadas: {mensalidades_criadas}")
    return mensalidades_criadas


# ================= GERENCIAMENTO DE PLANOS =================

def listar_planos():
    """Lista todos os planos ativos"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, nome, valor FROM planos WHERE ativo = 1 ORDER BY nome")
    planos = cur.fetchall()
    conn.close()
    return planos

def criar_plano(nome, valor):
    """Cria um novo plano"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO planos (nome, valor) VALUES (?, ?)", (nome, valor))
    conn.commit()
    conn.close()

def atualizar_plano(plano_id, nome, valor):
    """Atualiza um plano existente"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE planos SET nome = ?, valor = ? WHERE id = ?", (nome, valor, plano_id))
    conn.commit()
    conn.close()

def excluir_plano(plano_id):
    """Exclui (desativa) um plano"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE planos SET ativo = 0 WHERE id = ?", (plano_id,))
    conn.commit()
    conn.close()

def plano_existe(nome, plano_id=None):
    """Verifica se já existe um plano com o mesmo nome"""
    conn = get_conn()
    cur = conn.cursor()
    if plano_id:
        cur.execute("SELECT id FROM planos WHERE nome = ? AND id != ? AND ativo = 1", (nome, plano_id))
    else:
        cur.execute("SELECT id FROM planos WHERE nome = ? AND ativo = 1", (nome,))
    resultado = cur.fetchone()
    conn.close()
    return resultado is not None

def get_planos_formatados():
    """Retorna planos formatados para uso no ComboBox"""
    planos = listar_planos()
    planos_formatados = []
    for plano_id, nome, valor in planos:
        if valor == 0:
            planos_formatados.append(f"{nome}")
        else:
            planos_formatados.append(f"{nome} - R${valor:.0f}")
    
    # Adicionar opção personalizada
    planos_formatados.append("Plano Personalizado")
    
    return planos_formatados
