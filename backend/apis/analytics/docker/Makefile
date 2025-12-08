# Analytics Service Makefile

.PHONY: help build up down logs clean test lint format install

# デフォルトターゲット
help:
	@echo "Analytics Service - Available commands:"
	@echo "  build      - Build Docker images"
	@echo "  up         - Start services"
	@echo "  down       - Stop services"
	@echo "  logs       - Show container logs"
	@echo "  clean      - Remove containers and images"
	@echo "  test       - Run tests"
	@echo "  lint       - Run linter"
	@echo "  format     - Format code"
	@echo "  install    - Install dependencies with Poetry"

# Docker operations
build:
	@echo "Building Analytics service..."
	docker-compose build

up:
	@echo "Starting Analytics service..."
	docker-compose up -d
	@echo "Analytics API: http://localhost:8003"
	@echo "DynamoDB Local: http://localhost:8004"
	@echo "DynamoDB Admin: http://localhost:8005"

down:
	@echo "Stopping Analytics service..."
	docker-compose down

restart: down up

logs:
	docker-compose logs -f analytics-api

logs-all:
	docker-compose logs -f

# Cleanup operations
clean:
	@echo "Cleaning up Analytics service..."
	docker-compose down --volumes --remove-orphans
	docker-compose down --rmi local || true

clean-all: clean
	@echo "Removing all Analytics images..."
	docker images | grep analytics | awk '{print $$3}' | xargs docker rmi -f || true

# Development operations
install:
	@echo "Installing dependencies..."
	cd ../lambda && poetry install

test:
	@echo "Running tests..."
	cd ../lambda && poetry run pytest

test-watch:
	@echo "Running tests in watch mode..."
	cd ../lambda && poetry run pytest-watch

lint:
	@echo "Running linter..."
	cd ../lambda && poetry run flake8 src/
	cd ../lambda && poetry run mypy src/

format:
	@echo "Formatting code..."
	cd ../lambda && poetry run black src/
	cd ../lambda && poetry run isort src/

# Development setup
dev-setup: install
	@echo "Setting up development environment..."
	cd ../lambda && poetry run pre-commit install

# Database operations
init-db:
	@echo "Initializing DynamoDB Local..."
	cd ../../../scripts && poetry run python init_local_db.py

# Health checks
health:
	@echo "Checking Analytics service health..."
	@curl -f http://localhost:8003/health || echo "Service is down"

status:
	@echo "Analytics service status:"
	@docker-compose ps

# Production operations
deploy-lambda:
	@echo "Deploying Lambda function..."
	cd ../terraform && terraform plan
	cd ../terraform && terraform apply

package:
	@echo "Packaging Lambda function..."
	cd ../lambda && poetry build
	cd ../lambda && poetry export -f requirements.txt --output requirements.txt

# Monitoring
monitor:
	@echo "Monitoring Analytics service..."
	docker stats analytics-api

# Quick development cycle
dev: format lint test

# Full development cycle with Docker
full-dev: build up test

# Documentation
docs:
	@echo "Generating documentation..."
	@echo "Analytics API Documentation: http://localhost:8003/docs"