# Cloudry.in — Architecture Design

## Overview

Cloudry.in is a free online utility website offering PDF, image, and file tools. The architecture follows a split deployment model: static frontend served via GitHub Pages, and a Python backend API hosted on Render (free tier).

---

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      cloudry.in                          │
│                  (GitHub Pages + CDN)                    │
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │ PDF Unlocker│  │ Image→PDF   │  │ Compress    │    │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘    │
│         │                 │                 │           │
│         └─────────────────┼─────────────────┘           │
│                           │                             │
│              Cloudflare Turnstile (captcha)              │
│                           │                             │
└───────────────────────────┼─────────────────────────────┘
                            │ HTTPS API calls
                            ▼
┌─────────────────────────────────────────────────────────┐
│              api.cloudry.in (Render Free Tier)           │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │              FastAPI Application                   │   │
│  │                                                   │   │
│  │  ┌─────────┐ ┌─────────┐ ┌──────────────────┐   │   │
│  │  │ Router  │ │ Captcha │ │ Rate Limiter      │   │   │
│  │  │ Layer   │ │ Verify  │ │ (in-memory/Redis) │   │   │
│  │  └────┬────┘ └─────────┘ └──────────────────┘   │   │
│  │       │                                           │   │
│  │  ┌────▼────────────────────────────────────────┐  │   │
│  │  │           Service Layer                      │  │   │
│  │  │                                              │  │   │
│  │  │  pdf_service.py    image_service.py          │  │   │
│  │  │  qr_service.py     hash_service.py           │  │   │
│  │  │  markdown_service.py                         │  │   │
│  │  └──────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────┘   │
│                                                         │
│  Health: /health, /_admin/health/liveness               │
└─────────────────────────────────────────────────────────┘
```

---

## Tech Stack

### Backend (Python)

| Component | Choice | Reason |
|-----------|--------|--------|
| Framework | FastAPI | Async, fast, auto-docs, Pexa standard |
| Dependency mgmt | uv + pyproject.toml | Pexa standard, fastest resolver |
| Build system | hatchling | Pexa standard |
| Linting | ruff (line-length=120) | Pexa standard |
| Testing | pytest + pytest-cov (≥80%) | Pexa standard |
| Config | pydantic-settings + .env | Pexa standard |
| Logging | python-json-logger (structured) | Pexa standard |
| ASGI server | uvicorn | Production-ready |
| File uploads | python-multipart | Required by FastAPI |

### Frontend

| Component | Choice | Reason |
|-----------|--------|--------|
| HTML/CSS | Tailwind CSS (CDN) | Modern, responsive, no build step |
| Interactivity | Alpine.js | Lightweight (~15KB), no build step |
| Icons | Lucide Icons | Clean, MIT-licensed |
| Captcha | Cloudflare Turnstile | Free, privacy-friendly |
| Hosting | GitHub Pages | Free, custom domain support |

### Infrastructure

| Component | Choice | Reason |
|-----------|--------|--------|
| Backend hosting | Render (free tier) | Auto-deploy from GitHub, zero config |
| Frontend hosting | GitHub Pages | Free, fast CDN |
| DNS/CDN | Cloudflare (free) | DDoS protection, SSL, caching |
| CI/CD | GitHub Actions | Free 2000 min/month |
| Containers | Docker + Compose | Local dev parity |

---

## Project Structure

```
cloudry/
├── backend/
│   ├── src/
│   │   ├── __init__.py
│   │   ├── app.py                 # FastAPI app + health endpoints
│   │   ├── config.py              # pydantic-settings configuration
│   │   ├── logging_config.py      # Structured JSON logging
│   │   ├── middleware/
│   │   │   ├── __init__.py
│   │   │   ├── cors.py            # CORS for frontend
│   │   │   ├── rate_limiter.py    # Request rate limiting
│   │   │   └── captcha.py         # Turnstile verification
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── pdf.py             # PDF tool endpoints
│   │   │   ├── image.py           # Image tool endpoints
│   │   │   ├── qr.py              # QR code endpoints
│   │   │   ├── hash.py            # Hash calculator endpoints
│   │   │   └── markdown.py        # Markdown→PDF endpoints
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── pdf_service.py     # pikepdf, pypdf, pdf2image logic
│   │       ├── image_service.py   # Pillow, img2pdf logic
│   │       ├── qr_service.py      # qrcode generation
│   │       ├── hash_service.py    # hashlib operations
│   │       └── markdown_service.py # weasyprint conversion
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py            # Shared fixtures
│   │   ├── test_pdf.py
│   │   ├── test_image.py
│   │   ├── test_qr.py
│   │   ├── test_hash.py
│   │   ├── test_markdown.py
│   │   └── test_health.py
│   ├── pyproject.toml
│   ├── Makefile
│   ├── Dockerfile
│   ├── .env.example
│   ├── .coveragerc
│   └── .dockerignore
├── frontend/
│   ├── index.html                 # Main page with tool cards
│   ├── tools/
│   │   ├── pdf-unlock.html
│   │   ├── image-to-pdf.html
│   │   ├── image-compress.html
│   │   ├── pdf-merge.html
│   │   ├── pdf-split.html
│   │   ├── pdf-to-image.html
│   │   ├── image-convert.html
│   │   ├── pdf-watermark.html
│   │   ├── qr-generator.html
│   │   ├── file-hash.html
│   │   ├── markdown-to-pdf.html
│   │   └── image-resize.html
│   ├── assets/
│   │   ├── css/
│   │   │   └── style.css         # Custom styles (minimal)
│   │   ├── js/
│   │   │   ├── app.js            # Shared logic, API calls
│   │   │   ├── captcha.js        # Turnstile integration
│   │   │   └── tools/            # Per-tool JS if needed
│   │   └── img/
│   │       └── logo.svg
│   └── CNAME                     # cloudry.in
├── docker-compose.yml             # Local development
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                 # Lint, test, coverage
│   │   ├── cd-backend.yml         # Deploy backend to Render
│   │   └── cd-frontend.yml        # Deploy frontend to GitHub Pages
│   └── pull_request_template.md
├── Makefile                       # Top-level orchestration
├── README.md
└── LICENSE
```

---

## API Design

### Base URL: `https://api.cloudry.in`

### Endpoints

| Method | Endpoint | Description | Input | Output |
|--------|----------|-------------|-------|--------|
| POST | `/api/v1/pdf/unlock` | Remove PDF restrictions | PDF file + password (optional) | PDF file |
| POST | `/api/v1/pdf/merge` | Merge multiple PDFs | Multiple PDF files | PDF file |
| POST | `/api/v1/pdf/split` | Split PDF by pages | PDF file + page range | PDF file |
| POST | `/api/v1/pdf/to-image` | Convert PDF to images | PDF file + format | ZIP of images |
| POST | `/api/v1/pdf/watermark` | Add watermark to PDF | PDF file + watermark text | PDF file |
| POST | `/api/v1/pdf/compress` | Compress PDF file size | PDF file | PDF file |
| POST | `/api/v1/image/to-pdf` | Convert images to PDF | Image files | PDF file |
| POST | `/api/v1/image/compress` | Compress image | Image file + quality | Image file |
| POST | `/api/v1/image/resize` | Resize image | Image file + dimensions | Image file |
| POST | `/api/v1/image/convert` | Convert image format | Image file + target format | Image file |
| POST | `/api/v1/qr/generate` | Generate QR code | Text/URL + options | PNG/SVG file |
| POST | `/api/v1/hash/calculate` | Calculate file hash | File | JSON with hashes |
| POST | `/api/v1/markdown/to-pdf` | Convert markdown to PDF | Markdown text | PDF file |
| POST | `/api/v1/text/base64/encode` | Encode to Base64 | Text or file | JSON |
| POST | `/api/v1/text/base64/decode` | Decode from Base64 | Base64 string | JSON |
| POST | `/api/v1/text/json/format` | Pretty-print JSON | JSON string | JSON |
| POST | `/api/v1/text/json/validate` | Validate JSON | JSON string | JSON |
| POST | `/api/v1/text/color/convert` | Convert color format | Color + target format | JSON |
| GET | `/health` | Health check | — | JSON status |

### Common Headers

```
X-Turnstile-Token: <captcha_token>   # Required for all /api/v1/* endpoints
Content-Type: multipart/form-data     # For file uploads
```

### Rate Limiting

- 20 requests/minute per IP (free tier)
- File size limit: 20MB per file
- Max files per request: 10

### Response Format

Success: Returns the processed file directly with appropriate Content-Type and Content-Disposition headers.

Error:
```json
{
    "error": {
        "code": "FILE_TOO_LARGE",
        "message": "File size exceeds 20MB limit"
    }
}
```

---

## Security

1. **Captcha (Cloudflare Turnstile)** — Prevents bot abuse
2. **Rate limiting** — 20 req/min per IP
3. **File size limits** — 20MB max
4. **File type validation** — MIME type + magic bytes check
5. **Temp file cleanup** — Auto-delete after processing (no storage)
6. **CORS** — Only allow requests from cloudry.in
7. **No file persistence** — Files processed in-memory, never stored on disk

---

## Deployment Flow

```
Developer pushes code
        │
        ▼
GitHub Actions CI
├── Lint (ruff)
├── Test (pytest --cov, ≥80%)
├── Build Docker image
│
├── Frontend changed? → Deploy to GitHub Pages
└── Backend changed? → Render auto-deploys from main branch
```

---

## Local Development

```bash
# Start everything
docker compose up --build

# Backend: http://localhost:8000
# Frontend: http://localhost:3000 (or just open files)
# API docs: http://localhost:8000/docs
```

---

## DNS Configuration (Cloudflare)

| Type | Name | Target |
|------|------|--------|
| CNAME | cloudry.in | nitingadekar.github.io |
| CNAME | api | cloudry-api.onrender.com |

---

## Future Enhancements (Post-MVP)

- [ ] Redis for rate limiting (currently in-memory)
- [ ] File processing queue (for large files)
- [ ] Usage analytics (privacy-respecting)
- [ ] Dark mode toggle
- [ ] PWA support (offline QR generator, hash calculator)
- [ ] API keys for programmatic access

## Additional Tools (Phase 2)

| # | Category | Tool | Description |
|---|----------|------|-------------|
| 13 | PDF | Compress | Reduce PDF file size |
| 14 | Image | Crop | Crop images to selection |
| 15 | Text | Base64 Encode/Decode | Convert text/files to/from Base64 |
| 16 | Text | JSON Formatter | Pretty-print and validate JSON |
| 17 | Design | Color Picker/Converter | HEX↔RGB↔HSL conversion |
