#!/bin/bash
# scripts/validate_environment.sh

set -e

echo "🔍 VALIDAÇÃO COMPLETA DO AMBIENTE DE REPRODUÇÃO"
echo "=============================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Contadores
TESTS_PASSED=0
TESTS_FAILED=0

# Função para log de teste
log_test() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}❌ $2${NC}"
        ((TESTS_FAILED++))
    fi
}

# Função para log de aviso
log_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

echo "📋 1. VERIFICAÇÃO DE PRÉ-REQUISITOS"
echo "-----------------------------------"

# Verificar Docker
MIN_DOCKER_VERSION=20.10
DOCKER_VERSION=$(docker --version | awk '{print $3}' | sed 's/,//g' | cut -d. -f1,2)

# Converter versões para números inteiros para comparação
DOCKER_MAJOR=$(echo $DOCKER_VERSION | cut -d. -f1)
DOCKER_MINOR=$(echo $DOCKER_VERSION | cut -d. -f2)
DOCKER_INT=$((DOCKER_MAJOR * 100 + DOCKER_MINOR))

MIN_MAJOR=$(echo $MIN_DOCKER_VERSION | cut -d. -f1)
MIN_MINOR=$(echo $MIN_DOCKER_VERSION | cut -d. -f2)
MIN_INT=$((MIN_MAJOR * 100 + MIN_MINOR))

if [ $DOCKER_INT -ge $MIN_INT ]; then
    echo "✅ Docker versão suficiente: $DOCKER_VERSION"
else
    echo "❌ Docker versão insuficiente: $DOCKER_VERSION (mínimo: $MIN_DOCKER_VERSION)"
    exit 1
fi

# Verificar Docker Compose
if command -v docker-compose &> /dev/null; then
    log_test 0 "Docker Compose instalado"
else
    log_test 1 "Docker Compose não encontrado"
fi

# Verificar recursos do sistema
TOTAL_RAM=$(free -m | awk 'NR==2{printf "%.0f", $2/1024}')
if [ "$TOTAL_RAM" -ge 8 ]; then
    log_test 0 "RAM suficiente: ${TOTAL_RAM}GB"
else
    log_test 1 "RAM insuficiente: ${TOTAL_RAM}GB (mínimo: 8GB)"
fi

DISK_SPACE=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
if [ "$DISK_SPACE" -ge 10 ]; then
    log_test 0 "Espaço em disco suficiente: ${DISK_SPACE}GB"
else
    log_test 1 "Espaço em disco insuficiente: ${DISK_SPACE}GB (mínimo: 10GB)"
fi

echo -e "\n📊 2. VERIFICAÇÃO DE ARQUIVOS DO PROJETO"
echo "----------------------------------------"

# Verificar estrutura de arquivos
FILES_TO_CHECK=(
    "docker-compose.yml"
    "docker/Dockerfile"
    "scripts/requirements.txt"
    "scripts/calculate_metrics.py"
    "scripts/run_llm_analysis.py"
    "dataset/juice_shop_15_files.csv"
    "dataset/code_snippets"
)

for file in "${FILES_TO_CHECK[@]}"; do
    if [ -e "$file" ]; then
        log_test 0 "Arquivo/diretório encontrado: $file"
    else
        log_test 1 "Arquivo/diretório faltando: $file"
    fi
done

# Verificar snippets de código
SNIPPET_COUNT=$(find dataset/code_snippets -name "*.ts" | wc -l)
if [ "$SNIPPET_COUNT" -eq 15 ]; then
    log_test 0 "15 snippets de código encontrados"
else
    log_test 1 "Número incorreto de snippets: $SNIPPET_COUNT (esperado: 15)"
fi

echo -e "\n🚀 3. TESTE DE BUILD E INICIALIZAÇÃO"
echo "-----------------------------------"

# Build das imagens
echo "🏗️ Construindo imagens Docker..."
if docker-compose build --no-cache > /tmp/build.log 2>&1; then
    log_test 0 "Build das imagens Docker bem-sucedido"
else
    log_test 1 "Falha no build das imagens Docker"
    echo "📝 Últimas linhas do log de build:"
    tail -10 /tmp/build.log
fi

# Inicializar serviços
echo "🚀 Iniciando serviços..."
if docker-compose up -d > /tmp/up.log 2>&1; then
    log_test 0 "Serviços iniciados"
    sleep 30  # Aguardar estabilização
else
    log_test 1 "Falha ao iniciar serviços"
    echo "📝 Log de inicialização:"
    cat /tmp/up.log
fi

# Verificar status dos serviços
echo "🔍 Verificando status dos serviços..."
RUNNING_SERVICES=$(docker-compose ps --services --filter "status=running" | wc -l)
TOTAL_SERVICES=$(docker-compose ps --services | wc -l)

if [ "$RUNNING_SERVICES" -eq "$TOTAL_SERVICES" ]; then
    log_test 0 "Todos os serviços estão rodando ($RUNNING_SERVICES/$TOTAL_SERVICES)"
else
    log_test 1 "Alguns serviços não iniciaram ($RUNNING_SERVICES/$TOTAL_SERVICES)"
    echo "📊 Status detalhado:"
    docker-compose ps
fi

echo -e "\n🧪 4. TESTE MÍNIMO DE FUNCIONALIDADE"
echo "-----------------------------------"

# Teste do script principal
echo "📊 Executando teste mínimo..."
if docker-compose exec -T analysis python scripts/calculate_metrics.py dataset/juice_shop_15_files.csv > /tmp/test_output.log 2>&1; then
    log_test 0 "Script de cálculo de métricas executado com sucesso"
else
    log_test 1 "Falha na execução do script de métricas"
    echo "📝 Saída do teste:"
    cat /tmp/test_output.log
fi

# Verificar arquivos de resultado gerados
RESULT_FILES=(
    "results/metrics_table.csv"
    "results/metrics_table.html"
    "results/metrics_summary.json"
)

for result_file in "${RESULT_FILES[@]}"; do
    if docker-compose exec -T analysis test -f "$result_file"; then
        log_test 0 "Arquivo de resultado criado: $result_file"
    else
        log_test 1 "Arquivo de resultado faltando: $result_file"
    fi
done

echo -e "\n🤖 5. TESTE DE MODELOS LLM"
echo "-------------------------"

# Verificar se Ollama está funcionando
echo "🔍 Verificando Ollama..."
if docker-compose exec -T analysis curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    log_test 0 "Ollama API está respondendo"
else
    log_test 1 "Ollama API não está respondendo"
fi

# Verificar modelos instalados
echo "📥 Verificando modelos LLM..."
MODELS_OUTPUT=$(docker-compose exec -T analysis ollama list 2>/dev/null || echo "FAILED")

if echo "$MODELS_OUTPUT" | grep -q "deepseek-coder:1.3b"; then
    log_test 0 "Modelo DeepSeek Coder 1.3b instalado"
else
    log_test 1 "Modelo DeepSeek Coder 1.3b não encontrado"
    log_warning "Tentando instalar DeepSeek..."
    docker-compose exec -T analysis ollama pull deepseek-coder:1.3b || log_warning "Falha ao instalar DeepSeek"
fi

if echo "$MODELS_OUTPUT" | grep -q "codellama:7b"; then
    log_test 0 "Modelo CodeLlama 7b instalado"
else
    log_test 1 "Modelo CodeLlama 7b não encontrado"
    log_warning "Tentando instalar CodeLlama..."
    docker-compose exec -T analysis ollama pull codellama:7b || log_warning "Falha ao instalar CodeLlama"
fi

# Teste básico de inferência
echo "🧠 Testando inferência básica..."
DEEPSEEK_TEST=$(docker-compose exec -T analysis ollama run deepseek-coder:1.3b "print('hello')" 2>/dev/null | head -1 || echo "FAILED")
if [ "$DEEPSEEK_TEST" != "FAILED" ] && [ -n "$DEEPSEEK_TEST" ]; then
    log_test 0 "DeepSeek respondendo à inferência"
else
    log_test 1 "DeepSeek não está respondendo adequadamente"
fi

CODELLAMA_TEST=$(docker-compose exec -T analysis ollama run codellama:7b "print('hello')" 2>/dev/null | head -1 || echo "FAILED")
if [ "$CODELLAMA_TEST" != "FAILED" ] && [ -n "$CODELLAMA_TEST" ]; then
    log_test 0 "CodeLlama respondendo à inferência"
else
    log_test 1 "CodeLlama não está respondendo adequadamente"
fi

echo -e "\n🔍 6. TESTE DE FERRAMENTAS SAST"
echo "------------------------------"

# Verificar SonarQube
echo "🟦 Verificando SonarQube..."
for i in {1..10}; do
    if curl -s http://localhost:9000/api/system/status | grep -q "UP"; then
        log_test 0 "SonarQube está disponível em http://localhost:9000"
        break
    elif [ $i -eq 10 ]; then
        log_test 1 "SonarQube não está respondendo após 60s"
    else
        echo "⏳ Aguardando SonarQube... ($i/10)"
        sleep 6
    fi
done

# Verificar Semgrep
echo "🟢 Verificando Semgrep..."
if docker-compose exec -T semgrep semgrep --version > /dev/null 2>&1; then
    log_test 0 "Semgrep está funcional"
else
    log_test 1 "Semgrep não está funcionando"
fi

# Teste rápido do Semgrep
echo "🔍 Executando teste rápido do Semgrep..."
if docker-compose exec -T semgrep semgrep --config=auto /src/code_snippets/ --quiet > /tmp/semgrep_test.log 2>&1; then
    log_test 0 "Análise Semgrep executada com sucesso"
else
    log_test 1 "Falha na análise Semgrep"
    echo "📝 Log do Semgrep:"
    head -10 /tmp/semgrep_test.log
fi

echo -e "\n📊 7. VALIDAÇÃO DE DADOS E INTEGRIDADE"
echo "-------------------------------------"

# Verificar integridade do CSV
CSV_LINES=$(docker-compose exec -T analysis wc -l dataset/juice_shop_15_files.csv | cut -d' ' -f1)
if [ "$CSV_LINES" -eq 16 ]; then  # 15 linhas + header
    log_test 0 "CSV do ground truth tem o número correto de linhas (16)"
else
    log_test 1 "CSV do ground truth tem número incorreto de linhas: $CSV_LINES (esperado: 16)"
fi

# Verificar colunas obrigatórias no CSV
REQUIRED_COLUMNS=("ID" "File" "Vulnerability" "Is_Vulnerable" "Detected_Semgrep" "Detected_Sonar")
CSV_HEADER=$(docker-compose exec -T analysis head -1 dataset/juice_shop_15_files.csv)

for column in "${REQUIRED_COLUMNS[@]}"; do
    if echo "$CSV_HEADER" | grep -q "$column"; then
        log_test 0 "Coluna obrigatória encontrada: $column"
    else
        log_test 1 "Coluna obrigatória faltando: $column"
    fi
done

echo -e "\n🎯 8. TESTE DE REPRODUTIBILIDADE"
echo "-------------------------------"

# Executar o mesmo teste duas vezes e comparar
echo "🔄 Executando teste de reprodutibilidade..."
docker-compose exec -T analysis python scripts/calculate_metrics.py dataset/juice_shop_15_files.csv > /tmp/test1.log 2>&1
sleep 2
docker-compose exec -T analysis python scripts/calculate_metrics.py dataset/juice_shop_15_files.csv > /tmp/test2.log 2>&1

if diff /tmp/test1.log /tmp/test2.log > /dev/null; then
    log_test 0 "Resultados reproduzíveis (saídas idênticas)"
else
    log_test 1 "Resultados não reproduzíveis (saídas diferem)"
    echo "📝 Diferenças encontradas:"
    diff /tmp/test1.log /tmp/test2.log | head -10
fi

echo -e "\n🧹 9. LIMPEZA E RECURSOS"
echo "----------------------"

# Verificar uso de recursos
CONTAINER_COUNT=$(docker ps -q | wc -l)
echo "📊 Containers rodando: $CONTAINER_COUNT"

DISK_USAGE=$(docker system df --format "table {{.Type}}\t{{.TotalCount}}\t{{.Size}}")
echo "📊 Uso de disco Docker:"
echo "$DISK_USAGE"

# Oferecer limpeza
read -p "🗑️ Deseja limpar os containers e volumes? (y/N): " -r
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🧹 Limpando ambiente..."
    docker-compose down -v --remove-orphans
    docker system prune -f
    log_test 0 "Limpeza concluída"
fi

echo -e "\n📋 RELATÓRIO FINAL"
echo "=================="
echo -e "${GREEN}✅ Testes passaram: $TESTS_PASSED${NC}"
echo -e "${RED}❌ Testes falharam: $TESTS_FAILED${NC}"

TOTAL_TESTS=$((TESTS_PASSED + TESTS_FAILED))
SUCCESS_RATE=$((TESTS_PASSED * 100 / TOTAL_TESTS))

echo "📊 Taxa de sucesso: $SUCCESS_RATE%"

if [ "$SUCCESS_RATE" -ge 90 ]; then
    echo -e "${GREEN}🎉 AMBIENTE TOTALMENTE FUNCIONAL!${NC}"
    echo "✅ O artefato está pronto para avaliação"
    echo "📚 Próximos passos:"
    echo "  - make test-llm     # Análise LLM completa (30-80 min)"
    echo "  - make test-sast    # Ferramentas SAST (5-10 min)"
    echo "  - make validate     # Todos os testes"
elif [ "$SUCCESS_RATE" -ge 70 ]; then
    echo -e "${YELLOW}⚠️ AMBIENTE PARCIALMENTE FUNCIONAL${NC}"
    echo "🔧 Alguns problemas foram encontrados, mas o básico funciona"
    echo "📋 Revise os testes falhados acima"
else
    echo -e "${RED}❌ AMBIENTE COM PROBLEMAS CRÍTICOS${NC}"
    echo "🚨 Múltiplos testes falharam - revisão necessária"
    echo "📞 Consulte o guia de instalação ou documentação"
fi

echo -e "\n📁 Logs salvos em:"
echo "  - /tmp/build.log (build Docker)"
echo "  - /tmp/up.log (inicialização)"
echo "  - /tmp/test_output.log (teste principal)"

exit $TESTS_FAILED


echo -e "\n🔬 10. VERIFICAÇÃO DE RESULTADOS ESPERADOS"
echo "-----------------------------------"

compare_files() {
    diff -q "$1" "$2" >/dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "✅ $3: Resultados consistentes"
    else
        echo "❌ $3: Diferenças detectadas"
        echo "   Esperado: $2"
        echo "   Obtido:   $1"
        echo "   Diff:"
        diff "$1" "$2" | head -n 10
    fi
}

# Comparar métricas principais
compare_files "/app/results/metrics_table.csv" \
    "/app/results/expected/metrics_table.csv" \
    "Métricas Gerais"

# Comparar relatório contextual
compare_files "/app/results/contextual_validation_report.csv" \
    "/app/results/expected/contextual_validation_report.csv" \
    "Validação Contextual"

echo "✅ Verificação de resultados concluída!"