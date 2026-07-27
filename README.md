# Cloudry.in

> Free online utilities — PDF, Image, QR, and file tools. No signup, no storage, instant results.

**Live:** https://cloudry.in  
**API:** https://api.cloudry.in  
**Status:** 🚧 Under Development

---

## What is this?

A utility website offering 12+ free online tools:

| Category | Tools |
|----------|-------|
| PDF | Unlock, Merge, Split, To Image, Watermark |
| Image | To PDF, Compress, Resize, Format Convert |
| QR | QR Code Generator |
| Hash | MD5, SHA256 File Checksum |
| Markdown | Markdown to PDF |

## Architecture

- **Frontend:** Static HTML/CSS/JS (Tailwind CSS + Alpine.js) → GitHub Pages
- **Backend:** FastAPI (Python 3.13) → Render free tier
- **Captcha:** Cloudflare Turnstile
- **CI/CD:** GitHub Actions
- **Local Dev:** Docker Compose

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for full details.

## Quick Start (Local Development)

```bash
# Prerequisites: Docker + Docker Compose

# Start everything
docker compose up --build

# Backend: http://localhost:8000
# API docs: http://localhost:8000/docs
# Frontend: http://localhost:3000
```

## Backend Development

```bash
cd backend

# Install dependencies (requires uv)
make install

# Run tests
make test

# Lint
make lint

# Format check
make format

# Coverage (must be ≥80%)
make coverage

# Run locally
make run-local
```

## Project Structure

```
cloudry/
├── docs/                  # Architecture, decisions, context for AI tools
├── backend/               # FastAPI Python backend
│   ├── src/               # Application code
│   │   ├── middleware/    # CORS, rate limiting, captcha
│   │   ├── routers/       # API route handlers
│   │   └── services/      # Business logic (PDF, Image, etc.)
│   └── tests/             # pytest test suite
├── frontend/              # Static HTML/CSS/JS
│   ├── tools/             # Individual tool pages
│   └── assets/            # CSS, JS, images
├── .github/workflows/     # CI/CD pipelines
└── docker-compose.yml     # Local development
```

## Key Design Decisions

1. **No file storage** — Files processed in-memory, never persisted
2. **No user accounts (MVP)** — Captcha-only protection
3. **Rate limited** — 20 req/min per IP, 20MB file limit
4. **All libraries are free** — No paid/AGPL dependencies
5. **Split deployment** — Frontend and backend deploy independently

## Tech Stack

| Component | Tool | License |
|-----------|------|---------|
| PDF operations | pikepdf, pypdf | MPL-2.0, BSD |
| Image processing | Pillow, img2pdf | MIT-like, LGPL |
| PDF to Image | pdf2image + poppler | MIT |
| QR codes | qrcode | MIT |
| Markdown to PDF | weasyprint | BSD |
| File hashing | hashlib (stdlib) | PSF |
| API framework | FastAPI | MIT |
| Captcha | Cloudflare Turnstile | Free tier |

## Documentation

- [Architecture](docs/ARCHITECTURE.md) — System design, API spec, deployment
- [Research](docs/RESEARCH.md) — Library analysis, cost breakdown, alternatives
- [Decisions](docs/DECISIONS.md) — Why we chose what we chose
- [Monetization](docs/MONETIZATION.md) — Revenue model and growth plan
- [Deployment](docs/DEPLOYMENT.md) — How to deploy to production

## License

MIT
