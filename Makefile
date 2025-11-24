.PHONY: up down migrate seed fmt lint test

up:
docker-compose up -d --build

down:
docker-compose down

migrate:
docker-compose run --rm backend alembic upgrade head

seed:
python scripts/seed.py

fmt:
black backend

lint:
ruff backend

test:
pytest backend/tests
