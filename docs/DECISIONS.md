# Architectural Decisions

Record of key decisions made for the Cloudry.in project.

---

## ADR-001: Split Frontend/Backend Deployment

**Decision:** Host frontend on GitHub Pages, backend on Render (free tier).

**Context:** We need a backend for file processing (Python libraries can't run in browser). GitHub Pages is free but static-only.

**Alternatives considered:**
- Full-stack on Render: Would use up free tier for static files too
- Vercel + serverless functions: 10-second timeout too short for large file processing
- Client-side only (WASM): PDF/image JS libs are weaker, large files crash browsers

**Consequence:** Two deployment targets, CORS needed, but $0 cost and independent scaling.

---

## ADR-002: No User Accounts (MVP)

**Decision:** No signup/login for MVP. Use captcha + rate limiting instead.

**Context:** User accounts add complexity (auth, email verification, password reset, GDPR). For a utility site, most users want instant access.

**Consequence:** Can't offer persistent premium subscriptions easily. Will add accounts in Phase 3 if needed for payment integration.

---

## ADR-003: Cloudflare Turnstile over reCAPTCHA

**Decision:** Use Cloudflare Turnstile for bot protection.

**Reasons:**
- Privacy-friendly (no tracking, no data sold)
- No annoying image puzzles — invisible verification
- Free unlimited usage
- Aligns with site's "respect your privacy" positioning
- Cloudflare DNS already planned, so ecosystem synergy

---

## ADR-004: uv over pip/poetry for dependency management

**Decision:** Use `uv` with `pyproject.toml` and `uv.lock`.

**Reasons:**
- 10-100x faster than pip
- Deterministic lockfile
- Pexa team standard (familiar pattern)
- Built-in virtualenv management
- Hatchling build system compatibility

---

## ADR-005: No file persistence

**Decision:** Process files entirely in memory. Never write to disk, never store user files.

**Reasons:**
- Privacy: Users trust us because we don't keep their files
- Security: No data breach possible if there's no data
- Cost: No storage costs
- Compliance: No GDPR/data retention concerns
- Simplicity: No cleanup jobs, no storage management

**Implementation:** Use `io.BytesIO` for all file operations, return StreamingResponse directly.

---

## ADR-006: Render free tier with cold start accepted

**Decision:** Accept 30-second cold starts on Render free tier.

**Context:** Render free tier sleeps apps after 15 minutes of inactivity.

**Mitigation:**
- Frontend shows "Loading..." spinner during cold start
- Health check endpoint for quick wake-up
- Consider UptimeRobot ping every 14 minutes if cold starts become a problem (free tier allows it)

**When to upgrade:** If daily users exceed 100 or cold starts drive users away.

---

## ADR-007: Tailwind CSS + Alpine.js for frontend

**Decision:** Use Tailwind CSS (CDN) + Alpine.js instead of React/Vue/Next.js.

**Reasons:**
- No build step needed (CDN links)
- Static HTML = deployable on GitHub Pages directly
- Tailwind: Modern, responsive, utility-first CSS
- Alpine.js: 15KB, handles file uploads and interactivity
- SEO-friendly: Server-rendered HTML, fast load times
- Works on slow connections (rural India target)

**Tradeoff:** No client-side routing, each tool is a separate HTML page. This is fine for SEO (each page is independently indexable).

---

## ADR-008: Rate limiting strategy

**Decision:** In-memory rate limiting (20 req/min per IP) using `slowapi`.

**Context:** Can't use Redis on free tier. In-memory is fine for single-instance deployment.

**Limitation:** Rate limit resets on app restart/deploy. Acceptable for MVP.

**Upgrade path:** Add Redis when scaling to multiple instances.

---

## ADR-009: API versioning with /api/v1/ prefix

**Decision:** Version all API endpoints under `/api/v1/`.

**Reasons:**
- Allows breaking changes in future versions without affecting existing integrations
- Clean separation between health endpoints and business logic
- Standard practice for public APIs

---

## ADR-010: Monorepo structure

**Decision:** Single repo with `backend/` and `frontend/` folders.

**Reasons:**
- Simpler CI/CD (one repo to manage)
- Atomic changes across frontend + backend
- Shared documentation
- Easier for a solo developer

**Tradeoff:** Larger repo size, but irrelevant at our scale.

---

## ADR-011: Payment gateway choice (future)

**Decision:** Razorpay when payments are needed (Phase 3+).

**Reasons:**
- Works for individuals (no GST/company required)
- 2% fee only, no monthly cost
- UPI + cards + netbanking (Indian audience)
- Simple JS integration
- Stripe is invite-only in India and 6%+ for domestic

**Trigger:** Enable payments when daily active users > 100.
