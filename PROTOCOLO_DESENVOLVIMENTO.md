# 🔄 PROTOCOLO DE DESENVOLVIMENTO - Legacy BJJ

## 📋 **FLUXO OBRIGATÓRIO DE DESENVOLVIMENTO**

### **1️⃣ AJUSTE** 🛠️
- Implementar as mudanças solicitadas no código
- Seguir padrões estabelecidos do projeto
- Manter consistência com arquitetura existente

### **2️⃣ EXECUÇÃO** ▶️
```bash
./run.sh
```
- Verificar se o programa executa sem erros
- Testar funcionalidade implementada manualmente
- Confirmar que não há quebras visuais ou funcionais

### **3️⃣ TESTE INICIAL** 🧪
```bash
./t.sh
```
- Executar suite completa de testes
- Verificar se todos os 93+ testes passam
- Garantir que nenhuma funcionalidade existente foi quebrada

### **4️⃣ PROTOCOLO DE LIMPEZA** 🧹
#### **Verificações Obrigatórias:**
- **Código Duplicado**: Identificar e centralizar em utils/
- **Código Morto**: Remover funções/variáveis não utilizadas
- **Imports**: Verificar imports não utilizados
- **Arquivos Backup**: Remover .backup, .bak, .old, .tmp desnecessários
- **Arquivos .md**: Manter apenas README.md (excluir outros .md)
- **Comentários**: Manter apenas comentários úteis
- **.gitignore**: Atualizar se necessário

#### **Comandos de Verificação:**
```bash
# Buscar arquivos de backup
find . -name "*.backup" -o -name "*.bak" -o -name "*.old" -o -name "*~"

# Buscar arquivos .md desnecessários (manter apenas README.md)
find . -name "*.md" ! -name "README.md" ! -path "./node_modules/*"

# Verificar duplicação
grep -r "def " src/ | grep -v "__" | sort

# Buscar comentários TODO/FIXME
grep -r "TODO\|FIXME\|HACK\|BUG" src/
```

### **5️⃣ TESTE PÓS-LIMPEZA** ✅
```bash
./t.sh
```
- Executar testes novamente após limpeza
- Confirmar que limpeza não quebrou funcionalidades
- Validar que testes continuam 100% passando

### **6️⃣ COMMIT** 📝
```bash
git add -A
git commit -m "tipo: descrição clara

- Detalhe das mudanças implementadas
- Mencionar limpezas realizadas se houver
- Confirmar testes passando: X/X ✅"
```

#### **Tipos de Commit:**
- `feat:` Nova funcionalidade
- `fix:` Correção de bug
- `refactor:` Refatoração de código
- `style:` Mudanças de formatação
- `docs:` Documentação
- `test:` Testes
- `chore:` Tarefas de manutenção

### **7️⃣ PUSH** 🚀
```bash
git push
```
- Enviar mudanças para repositório remoto
- Confirmar que push foi bem-sucedido

---

## 🎯 **REGRAS FUNDAMENTAIS**

### **❌ NUNCA FAÇA:**
- Commit sem executar o protocolo completo
- Push sem confirmar que testes passam
- Mudanças que quebrem funcionalidades existentes
- Ignorar o protocolo de limpeza

### **✅ SEMPRE FAÇA:**
- Execute TODOS os passos na sequência
- Teste manualmente a funcionalidade
- Verifique que nenhum teste foi quebrado
- Limpe código sempre que possível
- Commit com mensagens descritivas

---

## 📊 **MÉTRICAS DE QUALIDADE**

### **Antes de Qualquer Commit:**
- ✅ **Programa executa** sem erros
- ✅ **Todos os testes** passando (93+)
- ✅ **Limpeza realizada** quando aplicável
- ✅ **Funcionalidade** testada manualmente
- ✅ **Commit message** descritiva

### **Meta de Qualidade:**
- 100% dos testes passando sempre
- Zero código duplicado
- Zero arquivos desnecessários
- Commits descritivos e organizados

---

## 🔧 **COMANDOS RÁPIDOS**

### **Protocolo Completo:**
```bash
# 1. Após fazer mudanças
./run.sh

# 2. Testes iniciais
./t.sh

# 3. Limpeza (se necessário)
find . -name "*.backup" -o -name "*.bak" | xargs rm -f
find . -name "*.md" ! -name "README.md" ! -path "./node_modules/*"

# 4. Testes finais
./t.sh

# 5. Commit e Push
git add -A
git commit -m "feat: sua mensagem aqui"
git push
```

### **Verificação Rápida:**
```bash
# Status do repositório
git status

# Diferenças
git diff

# Últimos commits
git log --oneline -5
```

---

## 📈 **VERSIONAMENTO**

**Versão**: 1.0
**Data**: 21 de Janeiro de 2026
**Autor**: Sistema Legacy BJJ

**Atualizações:**
- v1.0: Protocolo inicial com 7 etapas obrigatórias
- Inclusão do protocolo de limpeza como etapa obrigatória
- Definição de regras fundamentais e métricas de qualidade