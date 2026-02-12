.PHONY: help install dev test clean docker-build docker-run format lint

help:  ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies
	python -m pip install --upgrade pip
	pip install -r requirements.txt

dev:  ## Run development server
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:  ## Run tests
	pytest

test-cov:  ## Run tests with coverage
	pytest --cov=app --cov-report=html --cov-report=term

clean:  ## Clean up cache files
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete
	find . -type d -name '*.egg-info' -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov

docker-build:  ## Build Docker image
	docker build -t aiforge-backend .

docker-run:  ## Run Docker container
	docker run -p 8000:8000 --env-file .env aiforge-backend

docker-compose-up:  ## Start services with docker-compose
	docker-compose up --build

docker-compose-down:  ## Stop services with docker-compose
	docker-compose down

format:  ## Format code with black
	black app/ tests/

lint:  ## Lint code with ruff
	ruff check app/ tests/

setup:  ## Initial setup (install + env)
	./setup.sh
