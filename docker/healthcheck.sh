#!/bin/bash
# docker/healthcheck.sh

set -e

# Verificações básicas de saúde do container
HEALTH_STATUS=0

# 1. Verificar se Python está funcionando
if python3 --version > /dev/null 2>&1; then
    echo "✅ Python OK"
else
    echo "❌ Python falhou"
    HEALTH_STATUS=1
fi

# 2. Verificar se dependências Python estão instaladas
if python3 -c "import pandas, sklearn, numpy, ollama" > /dev/null 2>&1; then
    echo "✅ Dependências Python OK"
else
    echo "❌ Dependências Python faltando"
    HEALTH_STATUS=1
fi

# 3. Verificar se Ollama está rodando (se esperado)
if pgrep ollama > /dev/null 2>&1; then
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "✅ Ollama API OK"
    else
        echo "⚠️ Ollama processo rodando mas API não responde"
        HEALTH_STATUS=1
    fi
else
    echo "ℹ️ Ollama não está rodando (pode ser normal)"
fi

# 4. Verificar se diretórios necessários existem
if [ -d "/app/dataset" ] && [ -d "/app/scripts" ] && [ -d "/app/results" ]; then
    echo "✅ Diretórios necessários OK"
else
    echo "❌ Diretórios necessários faltando"
    HEALTH_STATUS=1
fi

# 5. Verificar se arquivos críticos existem
CRITICAL_FILES=(
    "/app/dataset/juice_shop_15_files.csv"
    "/app/scripts/calculate_metrics.py"
    "/app/scripts/run_llm_analysis.py"
)

for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file encontrado"
    else
        echo "❌ $file faltando"
        HEALTH_STATUS=1
    fi
done

# 6. Verificar snippets de código
SNIPPET_COUNT=$(find /app/dataset/code_snippets -name "*.ts" 2>/dev/null | wc -l || echo "0")
if [ "$SNIPPET_COUNT" -eq 15 ]; then
    echo "✅ 15 snippets de código encontrados"
else
    echo "❌ Número incorreto de snippets: $SNIPPET_COUNT (esperado: 15)"
    HEALTH_STATUS=1
fi

exit $HEALTH_STATUS