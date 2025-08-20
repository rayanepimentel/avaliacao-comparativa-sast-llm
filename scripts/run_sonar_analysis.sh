#!/bin/bash
# scripts/run_sonar_analysis.sh

set -e

echo "🔍 Executando análise SonarQube automatizada..."

# Configurações
SONAR_HOST="http://sonarqube:9000"
SONAR_LOGIN="admin"
SONAR_PASSWORD="admin"
PROJECT_KEY="juice-shop-analysis"
PROJECT_NAME="OWASP Juice Shop Analysis"

# Verificar se SonarQube está rodando
echo "📡 Verificando conectividade com SonarQube..."
for i in {1..30}; do
    if curl -s "$SONAR_HOST/api/system/status" | grep -q "UP"; then
        echo "✅ SonarQube está disponível!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Timeout aguardando SonarQube"
        exit 1
    fi
    echo "⏳ Aguardando SonarQube... ($i/30)"
    sleep 10
done

# Criar token de autenticação
echo "🔑 Criando token de autenticação..."
TOKEN_RESPONSE=$(curl -s -u "$SONAR_LOGIN:$SONAR_PASSWORD" \
    -X POST "$SONAR_HOST/api/user_tokens/generate" \
    -d "name=analysis-token")

TOKEN=$(echo "$TOKEN_RESPONSE" | grep -o '"token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo "❌ Falha ao criar token. Usando credenciais básicas."
    AUTH_TOKEN="$SONAR_LOGIN:$SONAR_PASSWORD"
else
    echo "✅ Token criado com sucesso!"
    AUTH_TOKEN="$TOKEN:"
fi

# Criar projeto se não existir
echo "📋 Configurando projeto SonarQube..."
curl -s -u "$AUTH_TOKEN" \
    -X POST "$SONAR_HOST/api/projects/create" \
    -d "project=$PROJECT_KEY" \
    -d "name=$PROJECT_NAME" || echo "Projeto já existe ou criado com sucesso"

# Instalar SonarScanner se não estiver instalado
if ! command -v sonar-scanner &> /dev/null; then
    echo "📥 Instalando SonarScanner..."
    wget -q https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-4.8.0.2856-linux.zip
    unzip -q sonar-scanner-cli-4.8.0.2856-linux.zip
    export PATH="$PWD/sonar-scanner-4.8.0.2856-linux/bin:$PATH"
fi

# Criar arquivo de configuração do SonarScanner
cat > sonar-project.properties << EOF
sonar.projectKey=$PROJECT_KEY
sonar.projectName=$PROJECT_NAME
sonar.projectVersion=1.0
sonar.sources=dataset/code_snippets
sonar.language=ts
sonar.sourceEncoding=UTF-8
sonar.host.url=$SONAR_HOST
sonar.login=$TOKEN
sonar.inclusions=**/*.ts
sonar.exclusions=**/node_modules/**,**/dist/**
EOF

# Executar análise
echo "🚀 Executando análise SonarQube..."
sonar-scanner \
    -Dsonar.projectKey="$PROJECT_KEY" \
    -Dsonar.sources="dataset/code_snippets" \
    -Dsonar.host.url="$SONAR_HOST" \
    -Dsonar.login="$TOKEN"

# Aguardar processamento
echo "⏳ Aguardando processamento da análise..."
sleep 30

# Obter resultados
echo "📊 Coletando resultados..."
ISSUES_RESPONSE=$(curl -s -u "$AUTH_TOKEN" \
    "$SONAR_HOST/api/issues/search?componentKeys=$PROJECT_KEY&types=VULNERABILITY&ps=500")

echo "$ISSUES_RESPONSE" > /app/results/sonarqube_issues.json

# Extrair estatísticas
TOTAL_ISSUES=$(echo "$ISSUES_RESPONSE" | grep -o '"total":[0-9]*' | head -1 | cut -d':' -f2)
CRITICAL_ISSUES=$(echo "$ISSUES_RESPONSE" | grep -o '"severity":"CRITICAL"' | wc -l)
MAJOR_ISSUES=$(echo "$ISSUES_RESPONSE" | grep -o '"severity":"MAJOR"' | wc -l)

echo "📈 Resultados da análise SonarQube:"
echo "  📊 Total de issues: $TOTAL_ISSUES"
echo "  🔴 Issues críticas: $CRITICAL_ISSUES"
echo "  🟠 Issues importantes: $MAJOR_ISSUES"
echo "  🌐 Relatório completo: http://localhost:9000/dashboard?id=$PROJECT_KEY"
echo "  📁 Arquivo JSON: /app/results/sonarqube_issues.json"
echo ""
echo "🔐 Credenciais de acesso:"
echo "  👤 Usuário: admin"
echo "  🔒 Senha: admin"
echo "  ⚠️  No primeiro login, é necessário alterar a senha"
echo ""
echo "✅ Análise SonarQube concluída!"