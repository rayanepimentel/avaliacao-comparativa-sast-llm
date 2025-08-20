#!/bin/bash
# docker/init-models.sh

set -e  # Parar em caso de erro

echo "🚀 Iniciando configuração do ambiente..."

# Verificar se Ollama está funcionando
echo "📡 Verificando Ollama..."
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama não encontrado!"
    exit 1
fi

# Iniciar serviço Ollama em background
echo "🔄 Iniciando serviço Ollama..."
ollama serve &
OLLAMA_PID=$!

# Aguardar Ollama estar pronto
echo "⏳ Aguardando Ollama ficar disponível..."
for i in {1..30}; do
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "✅ Ollama está pronto!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Timeout aguardando Ollama"
        exit 1
    fi
    sleep 2
done

# Baixar modelos necessários
echo "📥 Baixando modelo DeepSeek Coder 1.3B..."
if ! ollama pull deepseek-coder:1.3b; then
    echo "❌ Falha ao baixar deepseek-coder:1.3b"
    # Continuar mesmo se um modelo falhar
fi

echo "📥 Baixando modelo CodeLlama 7B..."
if ! ollama pull codellama:7b; then
    echo "❌ Falha ao baixar codellama:7b"
    # Continuar mesmo se um modelo falhar
fi

# Verificar modelos instalados
echo "📋 Modelos disponíveis:"
ollama list

# Testar modelos básicos
echo "🧪 Testando DeepSeek..."
if ollama run deepseek-coder:1.3b "print('hello')" 2>/dev/null | head -1; then
    echo "✅ DeepSeek funcionando"
else
    echo "⚠️ DeepSeek pode ter problemas"
fi

echo "🧪 Testando CodeLlama..."
if ollama run codellama:7b "print('hello')" 2>/dev/null | head -1; then
    echo "✅ CodeLlama funcionando"  
else
    echo "⚠️ CodeLlama pode ter problemas"
fi

echo "🎉 Configuração concluída!"
echo "📊 Execute: docker-compose exec analysis python scripts/calculate_metrics.py dataset/juice_shop_15_files.csv"

# Manter container rodando
tail -f /dev/null