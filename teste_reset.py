#!/usr/bin/env python3
"""
Script para testar o sistema de reset automático mensal
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database.db import get_conn

def verificar_configuracoes():
    """Verifica as configurações do sistema"""
    conn = get_conn()
    cur = conn.cursor()
    
    # Verificar se tabela existe
    cur.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='configuracoes'
    """)
    
    if cur.fetchone():
        print("✅ Tabela configuracoes existe")
        
        # Verificar conteúdo
        cur.execute("SELECT * FROM configuracoes")
        configs = cur.fetchall()
        
        if configs:
            print("📋 Configurações encontradas:")
            for config in configs:
                print(f"   {config[0]}: {config[1]}")
        else:
            print("⚠️ Tabela configuracoes está vazia")
    else:
        print("❌ Tabela configuracoes não existe")
    
    conn.close()

def listar_mensalidades_recentes():
    """Lista mensalidades do mês atual"""
    from datetime import date
    hoje = date.today()
    
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT m.id, a.nome, m.valor, m.data_vencimento, m.status, m.observacoes
        FROM mensalidades m
        JOIN alunos a ON m.aluno_id = a.id
        WHERE strftime('%m', m.data_vencimento) = ? 
        AND strftime('%Y', m.data_vencimento) = ?
        ORDER BY a.nome
    """, (f"{hoje.month:02d}", str(hoje.year)))
    
    mensalidades = cur.fetchall()
    
    print(f"\n📊 Mensalidades para {hoje.month:02d}/{hoje.year}:")
    if mensalidades:
        for mens in mensalidades:
            print(f"   {mens[1]} - R$ {mens[2]:.2f} - Venc: {mens[3]} - Status: {mens[4] or 'PENDENTE'}")
    else:
        print("   Nenhuma mensalidade encontrada para este mês")
    
    conn.close()

if __name__ == "__main__":
    print("🔍 Testando Sistema de Reset Automático\n")
    
    verificar_configuracoes()
    listar_mensalidades_recentes()
    
    print("\n✅ Teste concluído!")