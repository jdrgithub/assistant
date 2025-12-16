.PHONY: help install setup dev backend frontend docker-up docker-down init-db migrate

help:
	@echo "Available commands:"
	@echo "  make install     - Install all dependencies"
	@echo "  make setup       - Initial setup (copy .env, install deps)"
	@echo "  make dev         - Start development servers"
	@echo "  make backend     - Start backend only"
	@echo "  make frontend    - Start frontend only"
	@echo "  make docker-up   - Start Docker services"
	@echo "  make docker-down - Stop Docker services"
	@echo "  make init-db     - Initialize database"
	@echo "  make migrate     - Run database migrations"

install:
	./install_deps.sh
	cd frontend && npm install

setup: install
	@if [ ! -f .env ]; then cp .env.example .env; echo "Created .env file - please edit it!"; fi

docker-up:
	docker-compose -f docker/docker-compose.yml up -d

docker-down:
	docker-compose -f docker/docker-compose.yml down

init-db:
	poetry run python backend/scripts/init_db.py

migrate:
	poetry run alembic -c backend/alembic.ini upgrade head

backend:
	poetry run uvicorn backend.main:app --reload

frontend:
	cd frontend && npm run dev

dev: docker-up
	@echo "Starting development environment..."
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:3000"
	@make backend & make frontend

