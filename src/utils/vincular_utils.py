"""
Utilidades para vinculação de alunos - evita duplicação de código
"""

def vincular_aluno_responsavel(parent_widget):
    """
    Função utilitária para vincular aluno a responsável
    Usada por cadastro_aluno_tab, alunos_tab e financeiro_tab
    """
    from ui.app_dialog import show_input, show_error, show_warning, show_info
    
    # Solicitar CPF do aluno que será dependente
    cpf_dependente, ok = show_input(
        parent_widget, 
        "Vincular Dependente", 
        "Digite o CPF do aluno que será dependente:",
        "000.000.000-00"
    )
    
    if not ok or not cpf_dependente.strip():
        return False
        
    # Limpar CPF (remover caracteres especiais)
    cpf_dependente = ''.join(filter(str.isdigit, cpf_dependente.strip()))
    
    if len(cpf_dependente) != 11:
        show_error(parent_widget, "CPF Inválido", "O CPF deve ter 11 dígitos.")
        return False
    
    # Solicitar CPF do responsável
    cpf_responsavel, ok = show_input(
        parent_widget, 
        "Vincular Responsável", 
        "Digite o CPF do responsável:",
        "000.000.000-00"
    )
    
    if not ok or not cpf_responsavel.strip():
        return False
        
    # Limpar CPF (remover caracteres especiais)
    cpf_responsavel = ''.join(filter(str.isdigit, cpf_responsavel.strip()))
    
    if len(cpf_responsavel) != 11:
        show_error(parent_widget, "CPF Inválido", "O CPF do responsável deve ter 11 dígitos.")
        return False
        
    if cpf_dependente == cpf_responsavel:
        show_error(parent_widget, "CPF Inválido", "O dependente não pode ser responsável de si mesmo.")
        return False
        
    try:
        from database.db import get_conn
        conn = get_conn()
        cur = conn.cursor()
        
        # Verificar se existe o aluno dependente
        cur.execute("SELECT id, nome FROM alunos WHERE cpf = ? AND ativo = 1", (cpf_dependente,))
        dependente = cur.fetchone()
        
        if not dependente:
            show_error(parent_widget, "Aluno não encontrado", 
                      f"Não foi encontrado nenhum aluno ativo com o CPF: {cpf_dependente}")
            conn.close()
            return False
        
        # Verificar se existe um aluno adulto responsável com esse CPF
        cur.execute("SELECT id, nome FROM alunos WHERE cpf = ? AND ativo = 1", (cpf_responsavel,))
        responsavel = cur.fetchone()
        
        if not responsavel:
            show_error(parent_widget, "Responsável não encontrado", 
                      f"Não foi encontrado nenhum aluno adulto ativo com o CPF: {cpf_responsavel}")
            conn.close()
            return False
        
        responsavel_id, responsavel_nome = responsavel
        dependente_id, dependente_nome = dependente
        
        # Verificar se já não está vinculado
        cur.execute("SELECT responsavel_id FROM alunos WHERE id = ?", (dependente_id,))
        resultado = cur.fetchone()
        
        if resultado and resultado[0]:
            show_warning(parent_widget, "Já vinculado", f"O aluno {dependente_nome} já possui um responsável vinculado.")
            conn.close()
            return False
        
        # Vincular o aluno ao responsável
        cur.execute("UPDATE alunos SET responsavel_id = ? WHERE id = ?", (responsavel_id, dependente_id))
        
        # Sincronização de plano
        cur.execute("UPDATE alunos SET plano = ? WHERE id = ?", ("Vinculado ao responsável", dependente_id))
        
        conn.commit()
        conn.close()
        
        show_info(parent_widget, "Sucesso", f"Aluno {dependente_nome} vinculado com sucesso ao responsável: {responsavel_nome}")
        return True
            
    except Exception as e:
        show_error(parent_widget, "Erro", f"Erro ao vincular responsável: {str(e)}")
        return False