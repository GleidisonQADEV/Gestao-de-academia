# PROTOCOLO DE DESENVOLVIMENTO - Legacy BJJ

## FLUXO OBRIGATÓRIO DE DESENVOLVIMENTO

### 1. AJUSTE
- Implementar as mudanças solicitadas no código
- Seguir padrões estabelecidos do projeto (dark theme, objectName CSS, sem emojis)
- Manter consistência com arquitetura existente

### 2. EXECUÇÃO
```bash
./run.sh
```
- Verificar se o programa executa sem erros
- Testar funcionalidade implementada manualmente
- Confirmar que não há quebras visuais ou funcionais

### 3. TESTE INICIAL
```bash
./t.sh
```
- Executar suite completa de testes
- Verificar se todos os 82+ testes passam (3 skipped por ausência de reportlab — esperado)
- Garantir que nenhuma funcionalidade existente foi quebrada

### 4. VERIFICAÇÃO/CRIAÇÃO DE TESTES

#### Verificações Obrigatórias:
- **Cobertura**: Verificar se nova funcionalidade tem testes adequados
- **Casos de Teste**: Criar testes unitários para novas funções
- **Testes de Integração**: Verificar interações entre componentes
- **Casos Extremos**: Testar comportamentos limite e erros

#### Comandos de Verificação:
```bash
# Verificar se há arquivos de teste para nova funcionalidade
find tests/ -name "*nome_funcionalidade*"

# Executar testes específicos
python3 -m pytest tests/unit/test_nome.py -v

# Executar ignorando os testes UI que causam segfault em ambiente de CI
python3 -m pytest tests/ --ignore=tests/unit/test_cadastro_vinculacao_fixed.py --ignore=tests/unit/test_dashboard_ui.py -q
```

#### Ação Requerida:
- Se não existirem testes: **CRIAR** testes unitários mínimos
- Se existirem: **EXECUTAR** e verificar cobertura
- Garantir que edge cases estão cobertos

#### Notas de Isolamento de Testes:
- `test_ui_components.py` faz mock global do PySide6 — módulos que precisam do PySide6 real
  devem ser pré-importados no topo do arquivo de teste para garantir cache correto
- Testes de UI (PySide6 widgets) causam segfault fora de QApplication — ignorar em CI
- Testes que dependem de `reportlab` devem usar `pytest.importorskip('reportlab')`

### 5. PROTOCOLO DE LIMPEZA

#### Verificações Obrigatórias:
- **Código Duplicado**: Identificar e centralizar em utils/
- **Código Morto**: Remover funções/variáveis não utilizadas
- **Imports**: Verificar imports não utilizados
- **Arquivos Backup**: Remover .backup, .bak, .old, .tmp desnecessários

#### Comandos de Verificação:
```bash
# Buscar arquivos de backup
find . -name "*.backup" -o -name "*.bak" -o -name "*.old" -o -name "*~" | grep -v ".git"

# Buscar comentários TODO/FIXME
grep -r "TODO\|FIXME\|HACK" src/ --include="*.py"
```

### 6. TESTE PÓS-LIMPEZA
```bash
./t.sh
```
- Executar testes novamente após limpeza
- Confirmar que limpeza não quebrou funcionalidades
- Validar que testes continuam passando

### 7. COMMIT
```bash
git add <arquivos específicos>
git commit -m "tipo: descrição clara

- Detalhe das mudanças implementadas
- Mencionar limpezas realizadas se houver
- Confirmar testes passando: X/X"
```

#### Tipos de Commit:
- `feat:` Nova funcionalidade
- `fix:` Correção de bug
- `refactor:` Refatoração de código
- `style:` Mudanças de formatação/visual
- `docs:` Documentação
- `test:` Testes
- `chore:` Tarefas de manutenção

### 8. PUSH
```bash
git push
```

---

## REGRAS FUNDAMENTAIS

### NUNCA FAÇA:
- Commit sem executar o protocolo completo
- Push sem confirmar que testes passam
- Mudanças que quebrem funcionalidades existentes
- Usar `git add -A` sem revisar o que está sendo incluído

### SEMPRE FAÇA:
- Execute TODOS os passos na sequência
- Teste manualmente a funcionalidade
- Verifique que nenhum teste foi quebrado
- Commit com mensagens descritivas

---

## PADRÕES DE CÓDIGO - V1 (Dark Theme)

### CSS/Qt:
- Usar sempre `setObjectName()` + seletor `#nome { ... }` para evitar herança indesejada
- Nunca usar `QFrame { ... }` genérico — afeta widgets filhos
- Sem emojis em textos de UI ou mensagens de diálogo

### Dialogs:
- Usar `AppDialog` / `InputDialog` de `ui/app_dialog.py`
- `show_question`, `show_info`, `show_error`, `show_warning` — sem emojis nos títulos
- Botão primário (primeiro) = vermelho `#cc1e1e`, secundário = cinza `#1e1e1e`

### Versões V0/V1:
- V0 = versão backup com marca d'água (arquivos `*_v0.py`)
- V1 = versão redesign dark theme (arquivos sem sufixo)
- Toggle no sidebar reinicia o app via `os.execv`

---

## MÉTRICAS DE QUALIDADE

### Antes de Qualquer Commit:
- Programa executa sem erros
- 82+ testes passando (3 skipped esperados)
- Funcionalidade testada manualmente
- Commit message descritiva

---

## COMANDOS RÁPIDOS

```bash
# Rodar app
./run.sh

# Testes completos
./t.sh

# Testes sem UI segfault
python3 -m pytest tests/ --ignore=tests/unit/test_cadastro_vinculacao_fixed.py --ignore=tests/unit/test_dashboard_ui.py -q

# Status git
git status && git log --oneline -5
```

---

## VERSIONAMENTO

**Versão**: 2.0
**Data**: 29 de Abril de 2026
**Atualizações:**
- v1.0: Protocolo inicial com 7 etapas obrigatórias
- v2.0: Atualizado para refletir estado real do projeto:
  - Contagem de testes corrigida (82 passed, 3 skipped)
  - Adicionadas notas de isolamento de testes (mock PySide6, segfault)
  - Adicionados padrões de código V1 dark theme
  - Comandos atualizados para python3
  - Regras de CSS/Qt e dialogs documentadas
