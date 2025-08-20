.PHONY: help check-prereqs build up down test test-minimal test-llm test-sast test-contextual \
         clean logs shell quick-start validate reinit-models restart-sonarqube validate-env

# Comando padrão
help:
	@echo "🚀 COMANDOS DISPONÍVEIS:"
	@echo "  make build             - Construir imagens Docker"
	@echo "  make up                - Iniciar todos os serviços"
	@echo "  make down              - Parar todos os serviços"
	@echo "  make test              - Executar todos os testes (SAST + LLM + Métricas)"
	@echo "  make test-minimal      - Teste mínimo (gera Tabela 2 do artigo)"
	@echo "  make test-llm          - Análise completa com LLMs"
	@echo "  make test-sast         - Executar ferramentas SAST"
	@echo "  make test-contextual   - Validar recall de vulnerabilidades contextuais"
	@echo "  make validate          - Validação completa do ambiente e resultados"
	@echo "  make quick-start       - Setup rápido + teste mínimo"
	@echo "  make reinit-models     - Reinstalar modelos LLM (DeepSeek/CodeLlama)"
	@echo "  make restart-sonarqube - Reiniciar SonarQube"
	@echo "  make validate-env      - Validar ambiente com 86 verificações"
	@echo "  make logs              - Ver logs dos serviços"
	@echo "  make shell             - Acesso shell ao container principal"
	@echo "  make clean             - Limpar ambiente completamente"

# Verificar pré-requisitos de forma universal
check-prereqs:
	@echo "🔍 Verificando pré-requisitos..."
	@docker --version >/dev/null 2>&1 || ( \
		echo "❌ Docker não encontrado. Instale em: https://docs.docker.com/engine/install/"; \
		exit 1 \
	)
	@docker-compose --version >/dev/null 2>&1 || ( \
		echo "❌ Docker Compose não encontrado. Instale em: https://docs.docker.com/compose/install/"; \
		exit 1 \
	)
	@echo "✅ Docker e Docker Compose prontos!"
	@echo "ℹ️ Versão do Docker: $$(docker --version)"

# Construir ambiente
build: check-prereqs
	@echo "🏗️ Construindo imagens Docker..."
	docker-compose build
	@echo "✅ Build concluído!"

# Iniciar serviços
up: check-prereqs
	@echo "🚀 Iniciando serviços..."
	docker-compose up -d
	@echo "⏳ Aguardando inicialização (30 segundos)..."
	@sleep 30
	@echo "✅ Serviços iniciados!"
	@echo "• SonarQube: http://localhost:9000 (admin/admin)"
	@echo "• Ollama:    http://localhost:11434"
	@echo "• Resultados: ./results/"

# Parar serviços
down:
	@echo "🛑 Parando serviços..."
	docker-compose down

# Testes - CORRIGIDO: ordem correta das dependências
test: test-sast test-llm test-minimal test-contextual

test-minimal:
	@echo "🧪 EXECUTANDO TESTE MÍNIMO (Tabela 2 do artigo)..."
	docker-compose exec -T analysis python scripts/calculate_metrics.py dataset/juice_shop_15_files.csv
	@echo "📋 Verificando arquivos gerados..."
	@ls -l results/metrics_table.* || echo "⚠️ Arquivos de métricas não encontrados - verifique se test-sast e test-llm foram executados primeiro"
	@echo "✅ Teste mínimo concluído! Verifique ./results/"

test-llm:
	@echo "🤖 INICIANDO ANÁLISE LLM (30-80 minutos)..."
	docker-compose exec -T analysis python scripts/run_llm_analysis.py
	@echo "✅ Análise LLM concluída! Resultados: ./results/llm_detections_results.csv"

test-sast:
	@echo "🔍 EXECUTANDO FERRAMENTAS SAST..."
	@echo "🟢 Executando Semgrep..."
	docker-compose run --rm semgrep semgrep --config=auto /src/code_snippets/ --json --output=/results/semgrep_results.json
	@echo "🟦 Executando SonarQube..."
	docker-compose exec -T analysis bash scripts/run_sonar_analysis.sh
	@echo "✅ Análise SAST concluída!"
	@echo "• SonarQube: http://localhost:9000"
	@echo "• Semgrep:   ./results/semgrep_results.json"

test-contextual:
	@echo "🧠 VALIDANDO RECALL CONTEXTUAL..."
	docker-compose exec -T analysis python scripts/validate_contextual_recall.py
	@echo "✅ Validação contextual concluída!"

# Utilitários
logs:
	@echo "📜 EXIBINDO LOGS DOS SERVIÇOS..."
	docker-compose logs -f

shell:
	@echo "💻 ACESSANDO SHELL DO CONTAINER PRINCIPAL..."
	docker-compose exec analysis bash

# CORRIGIDO: Comando clean menos destrutivo
clean:
	@echo "🧹 LIMPANDO AMBIENTE..."
	docker-compose down -v --remove-orphans --rmi local
	docker network prune -f
	docker volume prune -f
	@echo "✅ Ambiente limpo!"

# Comandos avançados
quick-start: build up test-minimal
	@echo "🎉 INSTALAÇÃO RÁPIDA CONCLUÍDA!"
	@echo "📊 Próximos passos:"
	@echo "  make test-llm    # Análise LLM completa"
	@echo "  make test-sast   # Ferramentas SAST"
	@echo "  make validate    # Validação completa"

reinit-models:
	@echo "🔄 REINSTALANDO MODELOS LLM..."
	docker-compose exec -T analysis ollama rm deepseek-coder:1.3b || true
	docker-compose exec -T analysis ollama rm codellama:7b || true
	docker-compose exec -T analysis ollama pull deepseek-coder:1.3b
	docker-compose exec -T analysis ollama pull codellama:7b
	@echo "✅ Modelos reinstalados!"

restart-sonarqube:
	@echo "🔄 REINICIANDO SONARQUBE..."
	docker-compose restart sonarqube
	@echo "⏳ Aguardando reinicialização (20 segundos)..."
	@sleep 20
	@echo "✅ SonarQube reiniciado!"

validate:
	@echo "✅ VALIDAÇÃO COMPLETA INICIADA..."
	@make validate-env
	@make test
	@echo "✅✅ VALIDAÇÃO CONCLUÍDA COM SUCESSO!"
	@echo "📁 Resultados disponíveis em: ./results/"

validate-env:
	@echo "🔍 EXECUTANDO VALIDAÇÃO DE AMBIENTE (86 VERIFICAÇÕES)..."
	./scripts/validate_environment.sh