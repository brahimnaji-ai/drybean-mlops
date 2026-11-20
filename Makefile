.PHONY: install lint format typecheck test check up down down-v smoke

install:
	uv sync

lint:
	uv run ruff check .
	uv run ruff format --check .

format:
	uv run ruff format .
	uv run ruff check --fix .

typecheck:
	uv run mypy

test:
	uv run pytest

check: lint typecheck test

up:
	docker compose up -d --build --wait

down:
	docker compose down

down-v:
	docker compose down -v

smoke:
	bash scripts/smoke_stack.sh
