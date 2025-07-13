#!/bin/bash
# scripts/setup_models.sh

# Versões exatas usadas no artigo
OLLAMA_VERSION="v0.5.1"
DEEPSEEK_MODEL="deepseek-coder:1.3b"
CODELLAMA_MODEL="codellama:7b"

# Instalar Ollama
echo "Instalando Ollama ${OLLAMA_VERSION}..."
curl -fsSL https://ollama.com/install.sh | sh -s -- --version $OLLAMA_VERSION

# Verificar instalação
if ! command -v ollama &> /dev/null; then
    echo "❌ Falha na instalação do Ollama"
    exit 1
fi

# Baixar modelos
echo "Baixando modelo: ${DEEPSEEK_MODEL}..."
ollama pull $DEEPSEEK_MODEL

echo "Baixando modelo: ${CODELLAMA_MODEL}..."
ollama pull $CODELLAMA_MODEL

# Verificar modelos
echo "Modelos instalados:"
ollama list

echo "✅ Instalação completa!"