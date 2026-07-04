import sqlite3
import os
import sys
import shutil


def _resolver_db_path() -> str:
    """Retorna o caminho do banco em um diretório de dados persistente por-usuário.

    No executável onefile do PyInstaller, a pasta do módulo (__file__) fica dentro
    de um diretório temporário que é apagado ao fechar o app — o que fazia os dados
    cadastrados sumirem. Guardamos o banco fora desse temporário.
    """
    if sys.platform == "win32":
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
    elif sys.platform == "darwin":
        base = os.path.join(os.path.expanduser("~"), "Library", "Application Support")
    else:
        base = os.environ.get("XDG_DATA_HOME") or os.path.join(
            os.path.expanduser("~"), ".local", "share"
        )
    data_dir = os.path.join(base, "LegacyBJJ")
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, "legacy_bjj.db")


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = _resolver_db_path()

# Migração única: se ainda não existe banco persistente mas há um antigo ao lado
# do módulo (instalações/execuções anteriores), copia para preservar os dados.
_LEGACY_DB = os.path.join(BASE_DIR, "legacy_bjj.db")
if not os.path.exists(DB_PATH) and os.path.exists(_LEGACY_DB):
    try:
        shutil.copy2(_LEGACY_DB, DB_PATH)
    except Exception:
        pass


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

    # ---- tabela registros de presença ----
    cur.execute("""
        CREATE TABLE IF NOT EXISTS registros_presenca (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aluno_id INTEGER NOT NULL,
            data_registro DATE NOT NULL,
            hora_entrada TIME NOT NULL,
            hora_saida TIME,
            tipo_aluno TEXT NOT NULL, -- 'adulto' ou 'kid'
            biometria_usado INTEGER DEFAULT 0,
            observacoes TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (aluno_id) REFERENCES alunos (id)
        )
    """)
    
    # Criar índices para melhor performance
    cur.execute("CREATE INDEX IF NOT EXISTS idx_presenca_aluno_id ON registros_presenca(aluno_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_presenca_data ON registros_presenca(data_registro)")

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

    aluno_id = cur.lastrowid

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
    """Lista mensalidades de titulares de planos: adultos responsáveis e kids (exclui dependentes)."""
    conn = get_conn()
    cur = conn.cursor()

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
        # Verificar se já tem mensalidade no mês atual OU qualquer mensalidade recente
        cur.execute("""
            SELECT COUNT(*) FROM mensalidades 
            WHERE aluno_id = ? AND (
                strftime('%Y-%m', data_vencimento) = ? OR
                date(data_vencimento) >= date('now', '-30 days')
            )
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
                except Exception as e:
                    print(f"Erro ao criar mensalidade para {nome}: {e}")

    # Processar kids
    cur.execute("SELECT id, nome, plano FROM kids WHERE ativo = 1")
    kids = cur.fetchall()

    for kid_id, nome, plano in kids:
        # Verificar se já tem mensalidade no mês atual OU qualquer mensalidade recente
        cur.execute("""
            SELECT COUNT(*) FROM mensalidades
            WHERE aluno_id = ? AND (
                strftime('%Y-%m', data_vencimento) = ? OR
                date(data_vencimento) >= date('now', '-30 days')
            )
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
                except Exception as e:
                    print(f"Erro ao criar mensalidade para {nome} (Kids): {e}")
    
    conn.commit()
    conn.close()
    
    print(f"Total de mensalidades criadas: {mensalidades_criadas}")
    return mensalidades_criadas


def gerar_mensalidades_anuais(ano=None):
    """Gera mensalidades para todo o ano (12 meses) de uma vez"""
    from datetime import date
    import re
    
    if ano is None:
        ano = date.today().year
    
    conn = get_conn()
    cur = conn.cursor()
    
    mensalidades_criadas = 0
    
    # Processar alunos adultos (excluir dependentes)
    cur.execute("SELECT id, nome, plano FROM alunos WHERE ativo = 1 AND responsavel_id IS NULL")
    alunos = cur.fetchall()
    
    for aluno_id, nome, plano in alunos:
        # Gerar mensalidades para todos os 12 meses do ano
        for mes in range(1, 13):
            # Verificar se já tem mensalidade no mês
            cur.execute("""
                SELECT COUNT(*) FROM mensalidades 
                WHERE aluno_id = ? AND strftime('%Y-%m', data_vencimento) = ?
            """, (aluno_id, f"{ano}-{mes:02d}"))
            
            if cur.fetchone()[0] == 0:  # Não tem mensalidade no mês
                # Extrair valor do plano
                if plano and "R$0" not in plano and "Bolsista" not in plano and "Vinculado ao responsável" not in plano:
                    try:
                        match = re.search(r'R\$(\d+(?:\.\d{2})?)', plano)
                        if match:
                            valor = float(match.group(1))
                            data_vencimento = date(ano, mes, 10)

                            cur.execute("""
                                INSERT INTO mensalidades (aluno_id, valor, data_vencimento, status, observacoes)
                                VALUES (?, ?, ?, 'PENDENTE', ?)
                            """, (aluno_id, valor, data_vencimento, f'Mensalidade {mes:02d}/{ano} - {plano}'))
                            mensalidades_criadas += 1
                    except Exception as e:
                        print(f"Erro ao criar mensalidade anual para aluno {aluno_id} mês {mes}: {e}")

    # Processar kids
    cur.execute("SELECT id, nome, plano FROM kids WHERE ativo = 1")
    kids = cur.fetchall()

    for kid_id, nome, plano in kids:
        # Gerar mensalidades para todos os 12 meses do ano
        for mes in range(1, 13):
            # Verificar se já tem mensalidade no mês
            cur.execute("""
                SELECT COUNT(*) FROM mensalidades
                WHERE aluno_id = ? AND strftime('%Y-%m', data_vencimento) = ?
            """, (-kid_id, f"{ano}-{mes:02d}"))

            if cur.fetchone()[0] == 0:  # Não tem mensalidade no mês
                # Extrair valor do plano
                if plano and "R$0" not in plano and "Bolsista" not in plano and "Vinculado ao responsável" not in plano:
                    try:
                        match = re.search(r'R\$(\d+(?:\.\d{2})?)', plano)
                        if match:
                            valor = float(match.group(1))
                            data_vencimento = date(ano, mes, 10)

                            cur.execute("""
                                INSERT INTO mensalidades (aluno_id, valor, data_vencimento, status, observacoes)
                                VALUES (?, ?, ?, 'PENDENTE', ?)
                            """, (-kid_id, valor, data_vencimento, f'Mensalidade {mes:02d}/{ano} - {plano} (Kids)'))
                            mensalidades_criadas += 1
                    except Exception as e:
                        print(f"Erro ao criar mensalidade anual para kid {kid_id} mês {mes}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"Total de mensalidades anuais criadas para {ano}: {mensalidades_criadas}")
    return mensalidades_criadas


def obter_metricas_dashboard():
    """Obtém métricas para dashboard financeiro"""
    from datetime import date, timedelta
    
    conn = get_conn()
    cur = conn.cursor()
    
    hoje = date.today()
    inicio_mes = date(hoje.year, hoje.month, 1)
    if hoje.month == 12:
        fim_mes = date(hoje.year + 1, 1, 1) - timedelta(days=1)
    else:
        fim_mes = date(hoje.year, hoje.month + 1, 1) - timedelta(days=1)
    
    metricas = {}
    
    # Query base que exclui dependentes - ALINHADA COM listar_mensalidades
    base_query = """
        FROM mensalidades m
        LEFT JOIN alunos a ON m.aluno_id = a.id AND a.ativo = 1
        LEFT JOIN kids k ON m.aluno_id = -k.id AND k.ativo = 1
        WHERE (
            (a.id IS NOT NULL AND a.responsavel_id IS NULL) OR 
            (k.id IS NOT NULL)
        )
    """
    
    # 1. Mensalidades atrasadas
    cur.execute(f"""
        SELECT COUNT(*), COALESCE(SUM(m.valor), 0) 
        {base_query} 
        AND m.status = 'PENDENTE' AND m.data_vencimento < ?
    """, (hoje,))
    atrasadas_count, atrasadas_valor = cur.fetchone()
    metricas['atrasadas'] = {'count': atrasadas_count, 'valor': atrasadas_valor}
    
    # 2. Mensalidades pagas no mês
    cur.execute(f"""
        SELECT COUNT(*), COALESCE(SUM(m.valor), 0)
        {base_query}
        AND m.status = 'PAGO' AND m.data_pagamento BETWEEN ? AND ?
    """, (inicio_mes, fim_mes))
    pagas_count, pagas_valor = cur.fetchone()
    metricas['pagas_mes'] = {'count': pagas_count, 'valor': pagas_valor}
    
    # 3. Mensalidades a vencer (próximos 30 dias)
    proximos_30 = hoje + timedelta(days=30)
    cur.execute(f"""
        SELECT COUNT(*), COALESCE(SUM(m.valor), 0)
        {base_query}
        AND m.status = 'PENDENTE' AND m.data_vencimento BETWEEN ? AND ?
    """, (hoje, proximos_30))
    a_vencer_count, a_vencer_valor = cur.fetchone()
    metricas['a_vencer'] = {'count': a_vencer_count, 'valor': a_vencer_valor}
    
    # 4. Receita projetada anual
    cur.execute(f"""
        SELECT COALESCE(SUM(m.valor), 0)
        {base_query}
        AND strftime('%Y', m.data_vencimento) = ?
    """, (str(hoje.year),))
    receita_anual = cur.fetchone()[0]
    metricas['receita_anual'] = receita_anual
    
    # 5. Total de alunos
    cur.execute("SELECT COUNT(*) FROM alunos WHERE ativo = 1 AND responsavel_id IS NULL")
    alunos_responsaveis = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM alunos WHERE ativo = 1 AND responsavel_id IS NOT NULL")
    alunos_dependentes = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM kids WHERE ativo = 1")
    kids_count = cur.fetchone()[0]
    
    # Contar bolsistas (alunos com plano contendo "Bolsista")
    cur.execute("SELECT COUNT(*) FROM alunos WHERE ativo = 1 AND plano LIKE '%Bolsista%'")
    alunos_bolsistas = cur.fetchone()[0]
    
    # Contar kids bolsistas
    cur.execute("SELECT COUNT(*) FROM kids WHERE ativo = 1 AND plano LIKE '%Bolsista%'")
    kids_bolsistas = cur.fetchone()[0]
    
    total_bolsistas = alunos_bolsistas + kids_bolsistas
    
    metricas['alunos'] = {
        'responsaveis': alunos_responsaveis,
        'dependentes': alunos_dependentes,
        'kids': kids_count,
        'bolsistas': total_bolsistas,
        'total': alunos_responsaveis + alunos_dependentes + kids_count
    }
    
    # 6. Métricas de frequência
    metricas_freq = obter_metricas_frequencia()
    metricas.update(metricas_freq)
    
    conn.close()
    return metricas


def obter_status_pagamento_mes(ano=None, mes=None):
    """Returns {aluno_id: 'Pago'|'Atrasado'|'A Vencer'} for the given month (default: current)."""
    from datetime import date as _date
    if ano is None:
        _hoje = _date.today()
        ano, mes = _hoje.year, _hoje.month
    prox_mes = mes + 1 if mes < 12 else 1
    prox_ano = ano if mes < 12 else ano + 1
    inicio = f"{ano:04d}-{mes:02d}-01"
    fim = f"{prox_ano:04d}-{prox_mes:02d}-01"
    hoje_str = _date.today().isoformat()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT aluno_id, status, data_vencimento FROM mensalidades "
        "WHERE data_vencimento >= ? AND data_vencimento < ? ORDER BY data_vencimento ASC",
        (inicio, fim)
    )
    result = {}
    for aluno_id, status, data_venc in cur.fetchall():
        if aluno_id not in result:
            if status == 'PAGO':
                result[aluno_id] = 'Pago'
            elif data_venc and data_venc < hoje_str:
                result[aluno_id] = 'Atrasado'
            else:
                result[aluno_id] = 'A Vencer'
    conn.close()
    return result


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


# ================= GERENCIAMENTO DE PRESENÇA =================

def registrar_presenca(aluno_id, tipo_aluno='adulto', horario_aula=None, biometria_usado=False, observacoes=None):
    """Registra presença de um aluno em horário específico de aula"""
    from datetime import datetime
    
    conn = get_conn()
    cur = conn.cursor()
    
    agora = datetime.now()
    data_registro = agora.date()
    
    # Se não especificou horário, usar horário atual
    if horario_aula:
        hora_entrada = horario_aula
    else:
        hora_entrada = agora.time().strftime('%H:%M:%S')
    
    # Verificar se é dia de aula (segunda=0, quarta=2, sexta=4)
    dia_semana = data_registro.weekday()
    if dia_semana not in [0, 2, 4]:  # Segunda, Quarta, Sexta
        conn.close()
        return False, "Não é dia de aula (Segunda, Quarta ou Sexta)"
    
    # Verificar horários válidos de aula
    horarios_validos = ["08:30:00", "12:00:00", "18:30:00", "19:30:00"]
    if horario_aula and horario_aula not in horarios_validos:
        conn.close()
        return False, f"Horário inválido. Aulas: {', '.join(horarios_validos)}"
    
    # Verificar se já tem registro hoje no mesmo horário
    cur.execute("""
        SELECT id FROM registros_presenca 
        WHERE aluno_id = ? AND data_registro = ? AND tipo_aluno = ? AND hora_entrada = ?
    """, (aluno_id, data_registro, tipo_aluno, hora_entrada))
    
    if cur.fetchone():
        conn.close()
        return False, "Já registrado hoje neste horário"
    
    # Inserir novo registro
    cur.execute("""
        INSERT INTO registros_presenca 
        (aluno_id, data_registro, hora_entrada, tipo_aluno, biometria_usado, observacoes)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (aluno_id, data_registro, hora_entrada, tipo_aluno, int(biometria_usado), observacoes))
    
    conn.commit()
    conn.close()
    return True, "Presença registrada com sucesso"

def obter_metricas_frequencia():
    """Obtém métricas de frequência considerando apenas dias de aula"""
    from datetime import date, timedelta
    
    conn = get_conn()
    cur = conn.cursor()
    
    hoje = date.today()
    
    # Calcular últimos dias de aula
    def obter_dias_aula_periodo(data_fim, dias_periodo):
        dias_aula = []
        data_atual = data_fim
        
        while len(dias_aula) < dias_periodo:
            if data_atual.weekday() in [0, 2, 4]:  # Segunda, Quarta, Sexta
                dias_aula.append(data_atual)
            data_atual -= timedelta(days=1)
            
            # Evitar loop infinito
            if (data_fim - data_atual).days > 60:
                break
                
        return dias_aula
    
    # Últimos 5 dias de aula (aproximadamente 2 semanas)
    ultimos_dias_aula = obter_dias_aula_periodo(hoje, 5)
    data_inicio_periodo = min(ultimos_dias_aula) if ultimos_dias_aula else hoje - timedelta(days=14)
    
    metricas = {}
    
    # 1. Frequência de hoje (apenas se hoje for dia de aula)
    frequencia_hoje = 0
    if hoje.weekday() in [0, 2, 4]:
        cur.execute("""
            SELECT COUNT(DISTINCT r.aluno_id)
            FROM registros_presenca r
            LEFT JOIN alunos a ON r.aluno_id = a.id AND r.tipo_aluno = 'adulto' AND a.ativo = 1
            LEFT JOIN kids k ON r.aluno_id = k.id AND r.tipo_aluno = 'kid' AND k.ativo = 1
            WHERE r.data_registro = ? 
            AND ((a.id IS NOT NULL AND a.responsavel_id IS NULL) OR (k.id IS NOT NULL))
        """, (hoje,))
        frequencia_hoje = cur.fetchone()[0] or 0
    
    # 2. Frequência por horário hoje
    frequencia_horarios = {}
    if hoje.weekday() in [0, 2, 4]:
        horarios_aula = ["08:30:00", "12:00:00", "18:30:00", "19:30:00"]
        for horario in horarios_aula:
            cur.execute("""
                SELECT COUNT(*)
                FROM registros_presenca r
                LEFT JOIN alunos a ON r.aluno_id = a.id AND r.tipo_aluno = 'adulto' AND a.ativo = 1
                LEFT JOIN kids k ON r.aluno_id = k.id AND r.tipo_aluno = 'kid' AND k.ativo = 1
                WHERE r.data_registro = ? AND r.hora_entrada = ?
                AND ((a.id IS NOT NULL AND a.responsavel_id IS NULL) OR (k.id IS NOT NULL))
            """, (hoje, horario))
            count = cur.fetchone()[0] or 0
            frequencia_horarios[horario] = count
    
    # 3. Média de frequência nos últimos dias de aula
    if ultimos_dias_aula:
        placeholders = ','.join(['?'] * len(ultimos_dias_aula))
        cur.execute(f"""
            SELECT COUNT(DISTINCT r.aluno_id) / CAST({len(ultimos_dias_aula)} AS REAL)
            FROM registros_presenca r
            LEFT JOIN alunos a ON r.aluno_id = a.id AND r.tipo_aluno = 'adulto' AND a.ativo = 1
            LEFT JOIN kids k ON r.aluno_id = k.id AND r.tipo_aluno = 'kid' AND k.ativo = 1
            WHERE r.data_registro IN ({placeholders})
            AND ((a.id IS NOT NULL AND a.responsavel_id IS NULL) OR (k.id IS NOT NULL))
        """, ultimos_dias_aula)
        media_periodo = cur.fetchone()[0] or 0
    else:
        media_periodo = 0
    
    # 4. Total de alunos únicos no período
    if ultimos_dias_aula:
        placeholders = ','.join(['?'] * len(ultimos_dias_aula))
        cur.execute(f"""
            SELECT COUNT(DISTINCT r.aluno_id)
            FROM registros_presenca r
            LEFT JOIN alunos a ON r.aluno_id = a.id AND r.tipo_aluno = 'adulto' AND a.ativo = 1
            LEFT JOIN kids k ON r.aluno_id = k.id AND r.tipo_aluno = 'kid' AND k.ativo = 1
            WHERE r.data_registro IN ({placeholders})
            AND ((a.id IS NOT NULL AND a.responsavel_id IS NULL) OR (k.id IS NOT NULL))
        """, ultimos_dias_aula)
        alunos_ativos_periodo = cur.fetchone()[0] or 0
    else:
        alunos_ativos_periodo = 0
    
    # 5. Total de alunos cadastrados
    cur.execute("""
        SELECT 
            (SELECT COUNT(*) FROM alunos WHERE ativo = 1 AND responsavel_id IS NULL) +
            (SELECT COUNT(*) FROM kids WHERE ativo = 1)
    """)
    total_alunos = cur.fetchone()[0] or 0
    
    # 6. Percentual de aderência às aulas
    if total_alunos > 0:
        percentual_aderencia = (alunos_ativos_periodo / total_alunos) * 100
    else:
        percentual_aderencia = 0
    
    # 7. Horário mais movimentado
    horario_popular = "N/A"
    if frequencia_horarios:
        horario_popular = max(frequencia_horarios, key=frequencia_horarios.get)
        horario_popular = horario_popular[:5]  # Remover segundos (08:30)
    
    metricas['frequencia'] = {
        'hoje': frequencia_hoje,
        'eh_dia_aula': hoje.weekday() in [0, 2, 4],
        'media_periodo': round(media_periodo, 1),
        'alunos_ativos_periodo': alunos_ativos_periodo,
        'total_alunos': total_alunos,
        'percentual_aderencia': round(percentual_aderencia, 1),
        'frequencia_horarios': frequencia_horarios,
        'horario_popular': horario_popular,
        'dias_periodo': len(ultimos_dias_aula)
    }
    
    conn.close()
    return metricas
