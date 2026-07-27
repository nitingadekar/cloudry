# Deployment Guide

## Overview

| Component | Platform | URL |
|-----------|----------|-----|
| Frontend | GitHub Pages | https://cloudry.in |
| Backend | Render (free tier) | https://api.cloudry.in |
| DNS/CDN | Cloudflare (free) | — |

---

## 1. DNS Setup (Cloudflare)

### Prerequisites:
- Cloudflare account (free)
- Transfer nameservers from GoDaddy to Cloudflare

### DNS Records:

| Type | Name | Target | Proxy |
|------|------|--------|-------|
| CNAME | @ | nitingadekar.github.io | ✅ |
| CNAME | www | nitingadekar.github.io | ✅ |
| CNAME | api | cloudry-api.onrender.com | ✅ |

### Steps:
1. Sign up at cloudflare.com
2. Add site: cloudry.in
3. Cloudflare gives you 2 nameservers
4. Go to GoDaddy → Domain Settings → Nameservers → Change to Cloudflare's
5. Wait 24-48 hours for propagation
6. Add DNS records above in Cloudflare dashboard

---

## 2. Frontend Deployment (GitHub Pages)

### Setup:
1. Go to repo Settings → Pages
2. Source: GitHub Actions (or deploy from branch)
3. Custom domain: cloudry.in
4. Enforce HTTPS: ✅

### CNAME file:
The `frontend/CNAME` file contains `cloudry.in` — GitHub Pages uses this for custom domain binding.

### Auto-deploy:
The `cd-frontend.yml` workflow deploys frontend/ to GitHub Pages on push to main.

---

## 3. Backend Deployment (Render)

### Setup:
1. Sign up at render.com with GitHub
2. New → Web Service
3. Connect repo: nitingadekar/cloudry
4. Root directory: `backend`
5. Runtime: Docker
6. Instance type: Free
7. Branch: main (auto-deploy on push)

### Environment Variables (set in Render dashboard):

```
TURNSTILE_SECRET_KEY=<your-cloudflare-turnstile-secret>
CORS_ORIGINS=https://cloudry.in,https://www.cloudry.in
ENVIRONMENT=production
LOG_LEVEL=info
RATE_LIMIT_PER_MINUTE=20
MAX_FILE_SIZE_MB=20
```

### Custom Domain:
1. In Render dashboard → Settings → Custom Domains
2. Add: api.cloudry.in
3. It will verify via the CNAME record in Cloudflare

---

## 4. Cloudflare Turnstile Setup

1. Go to Cloudflare dashboard → Turnstile
2. Add site: cloudry.in
3. Widget mode: Managed (invisible when possible)
4. Get Site Key (for frontend) and Secret Key (for backend)
5. Add Secret Key to Render env vars

---

## 5. GitHub Actions Secrets

Set these in repo Settings → Secrets and variables → Actions:

| Secret | Purpose |
|--------|---------|
| `RENDER_DEPLOY_HOOK_URL` | Render deploy hook (optional, auto-deploy is on) |
| `TURNSTILE_SECRET_KEY` | For CI tests if needed |

---

## Local Development

```bash
# Clone and start
git clone git@github.com:nitingadekar/cloudry.git
cd cloudry
docker compose up --build

# Backend: http://localhost:8000
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

---

## Monitoring

### Free options:
- **UptimeRobot** — Ping api.cloudry.in/health every 5 minutes (also keeps Render warm)
- **Render dashboard** — Logs, metrics
- **Cloudflare Analytics** — Traffic, security events
- **Google Search Console** — SEO performance

---

## Scaling (When Needed)

| Trigger | Action | Cost |
|---------|--------|------|
| Cold starts annoying users | Upgrade Render to Starter ($7/mo) | $7/mo |
| > 100GB bandwidth/month | Cloudflare handles caching already | $0 |
| Need multiple instances | Add Redis for rate limiting, deploy 2nd instance | $10-15/mo |
| International users | Render has multi-region, or move to Fly.io | $5-10/mo |
