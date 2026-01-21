#!/bin/bash
# Script super rápido para testes - Legacy BJJ

# Cores
G='\033[0;32m'  # Green
B='\033[0;34m'  # Blue  
Y='\033[1;33m'  # Yellow
R='\033[0;31m'  # Red
N='\033[0m'     # No Color

echo -e "${B}🧪 Legacy BJJ - Testes Rápidos${N}"

# Definir Python correto (usa venv se disponível)
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    PYTHON="python"
else
    PYTHON="python3"
fi

# Verificar pytest
if ! $PYTHON -c "import pytest" 2>/dev/null; then
    echo -e "${Y}📦 Instalando pytest...${N}"
    $PYTHON -m pip install pytest pytest-cov >/dev/null 2>&1
fi

# Executar baseado no parâmetro
case "${1:-quick}" in
    "u"|"unit")
        echo -e "${B}🔬 Testes unitários...${N}"
        $PYTHON -m pytest tests/unit/ -q
        ;;
    "i"|"integration")  
        echo -e "${B}🔗 Testes integração...${N}"
        $PYTHON -m pytest tests/integration/ -q
        ;;
    "c"|"coverage")
        echo -e "${B}📊 Testes + cobertura...${N}"
        $PYTHON -m pytest tests/ --cov=src --cov-report=term-missing -q
        ;;
    "q"|"quick"|*)
        echo -e "${B}⚡ Testes rápidos...${N}"
        $PYTHON -m pytest tests/ -q --tb=line
        ;;
esac

# Resultado
if [ $? -eq 0 ]; then
    echo -e "${G}✅ Sucesso!${N}"
else
    echo -e "${R}❌ Falhas encontradas${N}"
    exit 1
fi