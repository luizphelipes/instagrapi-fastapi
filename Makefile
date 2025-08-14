.PHONY: help install dev test clean docker-build docker-up docker-down docker-logs

help: ## Mostra esta ajuda
	@echo "Instagram API FastAPI - Comandos disponíveis:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Instala dependências Python
	pip install -r requirements.txt

dev: ## Inicia a aplicação em modo desenvolvimento
	python start_dev.py

test: ## Executa testes
	pytest

test-cov: ## Executa testes com cobertura
	pytest --cov=. --cov-report=html

clean: ## Limpa arquivos temporários
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +

docker-build: ## Constrói as imagens Docker
	docker-compose build

docker-up: ## Inicia os serviços Docker
	docker-compose up -d

docker-down: ## Para os serviços Docker
	docker-compose down

docker-logs: ## Mostra logs dos serviços Docker
	docker-compose logs -f

docker-restart: ## Reinicia os serviços Docker
	docker-compose restart

docker-clean: ## Remove containers e volumes Docker
	docker-compose down -v --remove-orphans

docker-clean-all: ## Limpa completamente o ambiente Docker
	docker-compose down -v --remove-orphans --rmi all

docker-fresh: ## Limpa tudo e reconstrói do zero
	docker-compose down -v --remove-orphans --rmi all
	docker-compose up --build

format: ## Formata código com black
	black .

lint: ## Executa linting com flake8
	flake8 .

type-check: ## Verifica tipos com mypy
	mypy .

security-check: ## Verifica vulnerabilidades de segurança
	safety check

all-checks: format lint type-check security-check ## Executa todas as verificações

setup-dev: install ## Configura ambiente de desenvolvimento
	@echo "✅ Ambiente de desenvolvimento configurado!"
	@echo "📝 Configure o arquivo .env com suas variáveis"
	@echo "🚀 Execute 'make dev' para iniciar a aplicação"

setup-docker: docker-build ## Configura ambiente Docker
	@echo "✅ Ambiente Docker configurado!"
	@echo "🚀 Execute 'make docker-up' para iniciar os serviços"

reset-docker: docker-clean-all docker-build ## Reseta completamente o ambiente Docker
	@echo "🔄 Ambiente Docker resetado!"
	@echo "🚀 Execute 'make docker-up' para iniciar os serviços" 