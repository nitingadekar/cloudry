.PHONY: install test lint format coverage run-local build clean

UV_VERSION := 0.11.2
UV := $(shell command -v uv 2>/dev/null)

install:
ifndef UV
	curl -LsSf https://astral.sh/uv/$(UV_VERSION)/install.sh | sh
	$(eval UV := $(HOME)/.local/bin/uv)
endif
	$(UV) sync

test:
	uv run pytest tests/ -v

lint:
	uv run ruff check src/ tests/

format:
	uv run ruff format --check src/ tests/

coverage:
	uv run pytest tests/ --cov=src --cov-report=xml --cov-report=term
	uv run coverage report --fail-under=80

run-local:
	uv run uvicorn src.app:app --reload --host 0.0.0.0 --port 8000

build:
	docker build -t cloudry-backend .

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	rm -f coverage.xml .coverage
