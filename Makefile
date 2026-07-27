.PHONY: dev stop test lint backend frontend

# Start full local dev stack
dev: backend frontend
	@echo "✅ Cloudry running locally:"
	@echo "   Frontend: http://localhost:3000"
	@echo "   Backend:  http://localhost:8000"
	@echo "   API Docs: http://localhost:8000/docs"

backend:
	cd backend && uv run uvicorn src.app:app --reload --host 0.0.0.0 --port 8000 &

frontend:
	cd frontend && python3 -m http.server 3000 &

stop:
	-pkill -f "uvicorn src.app:app" 2>/dev/null
	-pkill -f "http.server 3000" 2>/dev/null
	@echo "Stopped all services"

test:
	cd backend && uv run pytest tests/ -v

lint:
	cd backend && uv run ruff check src/ tests/

coverage:
	cd backend && uv run pytest tests/ --cov=src --cov-report=term

docker:
	docker compose up --build
