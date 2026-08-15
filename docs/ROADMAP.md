# Cloudry.in — Roadmap & Action Plan

> Last updated: 2026-08-15
> Status: MVP Live + AI Caption Generator shipped

---

## ✅ Completed

### Phase 1: MVP (Core Utilities)
- [x] PDF tools: unlock, merge, split, to-image, watermark, compress
- [x] Image tools: to-pdf, compress, resize, convert
- [x] QR code generator (PNG + SVG)
- [x] File hash calculator (MD5, SHA1, SHA256)
- [x] Markdown to PDF converter
- [x] Developer tools: JSON formatter, Base64 encode/decode, color converter
- [x] Cloudflare Turnstile captcha protection
- [x] Rate limiting (20 req/min)
- [x] CI/CD pipeline (lint, test, coverage)
- [x] Frontend on GitHub Pages + Backend on Render.com
- [x] PDF input validation (friendly errors for invalid/encrypted files)

### Phase 1.5: AI Feature
- [x] AI Caption Generator (Groq API, Qwen 3.6 27B multimodal)
- [x] 12 themes, 6 languages (Romanized script)
- [x] Backend warm-up workflow (8am IST daily cron)
- [x] Prompt guardrails (ignore image text injection, safety filters)
- [x] One-shot generation per upload (prevents API abuse)
- [x] UPI payment integration for premium regeneration (₹20)

> **Code frozen: 2026-08-15** — Stabilization complete. Next focus: marketing & traffic.

---

## 🔥 Next Up (Priority Order)

### 1. Homepage Redesign — Make It Fun
- [ ] Add interactive/animated elements (particle effects, typing animations)
- [ ] Easter eggs or micro-interactions that make people revisit
- [ ] "Try me" instant demo without file upload (e.g., live QR preview)
- [ ] Better hero section with animated tool showcase
- Goal: Increase organic return visits and time-on-site

### 2. YAML Linter Tool
- [ ] Backend: validate YAML, return errors with line numbers
- [ ] Library: `ruamel.yaml` (MIT, better error messages than pyyaml)
- [ ] Frontend: text area input, real-time validation, error highlighting
- [ ] Add to "Developer Tools" section

### 3. Tech DevOps Utilities
- [ ] **K8s YAML Generator** (form-based)
  - Deployment, Service, Ingress, ConfigMap templates
  - Dropdown for common patterns (web app, worker, cron)
  - Free — no AI, just templating
- [ ] **Dockerfile Generator** (form-based)
  - Select language/framework → get best-practice Dockerfile
  - Multi-stage builds, security hardening included
  - Free — template engine
- [ ] **AI Dockerfile Generator** (NLP input)
  - "I have a Python FastAPI app with Redis and PostgreSQL" → complete Dockerfile + docker-compose
  - Uses Groq API (charged service after free tier exhausted)
- [ ] **AI K8s Manifest Generator**
  - Describe your app in natural language → full K8s manifests
  - Charged: ₹20/generation via Razorpay

### 4. Caption Generator Enhancements
- [ ] Video support (extract key frames with ffmpeg → same pipeline)
- [ ] Per-user daily limit tracking (5 free/day, then ₹20/use)
- [ ] "Share to Instagram" deep link
- [ ] Caption history (in-browser localStorage, not server-side)

### 5. Monetization (when traffic justifies)
- [ ] Razorpay integration (₹20/use for AI tools, ₹99/month premium)
- [ ] Ad placement (Google AdSense — non-intrusive)
- [ ] API access tier (₹499/month for developers)
- Trigger: 100+ daily active users

### 6. Marketing & Growth
- [ ] WhatsApp/Telegram group marketing blitz
- [ ] "Break the site" challenge campaign
- [ ] Product Hunt launch
- [ ] SEO: Hindi keyword pages
- [ ] YouTube shorts: "How to unlock PDF online"

---

## 🏗️ Technical Debt & Improvements

- [ ] Replace Tailwind CDN with pre-compiled CSS (suppress console warning, improve load performance)
- [ ] Redis for rate limiting (currently in-memory, resets on deploy)
- [ ] Structured error responses (standardize error JSON format)
- [ ] Request ID tracking (correlation across logs)
- [ ] Dark mode toggle
- [ ] PWA support (offline QR generator, hash calculator)
- [ ] Image EXIF stripping (privacy feature)
- [ ] PDF OCR (extract text from scanned PDFs — may need tesseract)

---

## 💡 Idea Backlog (Unvalidated)

| Idea | Type | Cost | Priority |
|------|------|------|----------|
| YAML linter | Dev tool | Free (ruamel.yaml) | High |
| K8s YAML generator | DevOps template | Free | Medium |
| Dockerfile generator | DevOps template | Free | Medium |
| AI Dockerfile from NLP | AI tool | Groq free → paid | Medium |
| AI K8s manifests | AI tool | Paid (₹20/use) | Low |
| Video captions | AI extension | Groq + ffmpeg | Medium |
| Aadhaar PDF unlocker | India-specific | Free (pikepdf) | High |
| UPI QR generator | India-specific | Free (qrcode) | High |
| Resume PDF builder | Template tool | Free (reportlab) | Low |
| Code screenshot | Dev tool | Free (Pillow) | Low |
| Regex tester | Dev tool | Free (re stdlib) | Medium |

---

## 📊 Key Metrics to Track

| Metric | Current | Target (3 months) |
|--------|---------|-------------------|
| Daily visitors | ~5 | 200+ |
| Tools available | 17 | 25+ |
| Test coverage | 80%+ | 85%+ |
| Cold start time | ~30s | <5s (warm-up cron) |
| Monthly cost | $0 | $0 (until 100 DAU) |

---

## 🤖 Agent Context (for new dev sessions)

### How this project works:
1. **Frontend**: Static HTML + Tailwind CSS + Alpine.js → hosted on GitHub Pages (cloudry.in)
2. **Backend**: FastAPI + Python → hosted on Render.com free tier (api.cloudry.in)
3. **AI**: Groq API free tier for caption generation (GROQ_API_KEY in Render env vars)
4. **All file processing is in-memory** (io.BytesIO) — never stored on disk
5. **Cost: $0/month** — all infrastructure is free tier

### Git workflow:
- Personal project: `gh auth switch --user nitingadekar`
- Work profile: `gh auth switch --user nitingadekar-pexa`
- Always switch back to pexa after pushing
- GPG signing enabled globally — use `--no-gpg-sign` for commits
- Push to feature branch → create PR → merge → auto-deploys

### Key files to read first:
- `docs/ARCHITECTURE.md` — full system design
- `docs/DECISIONS.md` — ADRs explaining why choices were made
- `docs/MONETIZATION.md` — revenue plan
- `backend/src/app.py` — FastAPI app entry point
- `backend/src/services/` — all business logic
- `frontend/tools/` — individual tool pages

### Testing:
- `cd backend && uv run pytest` — run all tests
- `cd backend && uv run ruff check src/ tests/` — lint
- Tests mock external APIs (Groq) — no real API calls in CI
- `TURNSTILE_ENABLED=false` in test env — captcha bypassed
