#!/usr/bin/env python3
"""
Script para limpar os dados do banco de dados
Mantém as estruturas das tabelas mas remove todos os registros de alunos
"""

import sqlite3
import os

# Caminho para o banco de dados
db_path = os.path.join('src', 'database', 'legacy_bjj.db')

def limpar_banco():
    """Limpa todos os alunos do banco de dados"""
    
    if not os.path.exists(db_path):
        print(f"❌ Banco de dados não encontrado: {db_path}")
        return
    
    print(f"🗃️  Conectando ao banco: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        
        # Verificar quantos registros existem antes
        cur.execute("SELECT COUNT(*) FROM alunos")
        count_adultos = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM kids")
        count_kids = cur.fetchone()[0]
        
        print(f"📊 Registros encontrados:")
        print(f"   • Adultos: {count_adultos}")
        print(f"   • Kids: {count_kids}")
        print(f"   • Total: {count_adultos + count_kids}")
        
        if count_adultos == 0 and count_kids == 0:
            print("✅ Banco já está vazio!")
            return
        
        # Confirmar antes de apagar
        resposta = input("\n❓ Deseja realmente apagar TODOS os alunos? (digite 'SIM' para confirmar): ")
        
        if resposta.upper() != 'SIM':
            print("❌ Operação cancelada.")
            return
        
        # Limpar tabelas
        print("\n🧹 Limpando dados...")
        cur.execute("DELETE FROM alunos")
        cur.execute("DELETE FROM kids")
        
        # Resetar auto-increment
        cur.execute("DELETE FROM sqlite_sequence WHERE name='alunos'")
        cur.execute("DELETE FROM sqlite_sequence WHERE name='kids'")
        
        conn.commit()
        print("✅ Todos os alunos foram removidos!")
        print("✅ IDs foram resetados para começar do 1")
        
        # Verificar se realmente foi limpo
        cur.execute("SELECT COUNT(*) FROM alunos")
        count_adultos = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM kids")
        count_kids = cur.fetchone()[0]
        
        print(f"\n📊 Registros após limpeza:")
        print(f"   • Adultos: {count_adultos}")
        print(f"   • Kids: {count_kids}")
        print(f"   • Total: {count_adultos + count_kids}")
        
    except Exception as e:
        print(f"❌ Erro ao limpar banco: {e}")
    
    finally:
        if conn:
            conn.close()
            print("🔒 Conexão fechada.")

if __name__ == "__main__":
    print("🧹 === LIMPADOR DE BANCO DE DADOS ===")
    print("Este script remove TODOS os alunos cadastrados")
    print("Mantém apenas as estruturas das tabelas\n")
    
    limpar_banco()
    
    print("\n🎯 Para testar:")
    print("1. Execute: python3 src/main.py")
    print("2. Faça login (admin/admin)")  
    print("3. Cadastre alguns alunos")
    print("4. Teste a aba 'Alunos' e a pesquisa")