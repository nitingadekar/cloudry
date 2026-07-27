# Library Research & Cost Analysis

> All recommended libraries are 100% FREE for commercial use. No subscriptions required.

## Recommended Stack

| Utility | Library | PyPI Package | License | Free? |
|---------|---------|-------------|---------|-------|
| PDF Unlocker | pikepdf | `pikepdf` | MPL-2.0 | ✅ YES |
| Image → PDF | img2pdf | `img2pdf` | LGPL-3.0 | ✅ YES |
| Image Compress/Resize | Pillow | `Pillow` | HPND (MIT-like) | ✅ YES |
| PDF Merge | pypdf | `pypdf` | BSD-3-Clause | ✅ YES |
| PDF Split | pypdf | `pypdf` | BSD-3-Clause | ✅ YES |
| PDF → Image | pdf2image | `pdf2image` | MIT | ✅ YES |
| Image Format Convert | Pillow | `Pillow` | HPND (MIT-like) | ✅ YES |
| PDF Watermark | pikepdf + reportlab | `pikepdf` + `reportlab` | MPL-2.0 + BSD | ✅ YES |
| QR Code | qrcode | `qrcode` | MIT | ✅ YES |
| File Hash | hashlib | stdlib | PSF | ✅ YES |
| Markdown → PDF | WeasyPrint | `weasyprint` | BSD-3-Clause | ✅ YES |
| CAPTCHA | Cloudflare Turnstile | REST API | Free tier | ✅ YES |

## Libraries to AVOID

| Library | Issue |
|---------|-------|
| **PyMuPDF (fitz)** | AGPL-3.0 — must open-source your code OR buy commercial license from Artifex |
| **ReportLab PLUS** | Paid commercial edition (community edition is fine) |
| **Adobe PDF SDK** | Fully paid/proprietary |
| **PDFtk Pro** | Paid version (PDFtk Server is GPL — copyleft concerns) |

## Detailed Library Notes

### pikepdf (PDF Unlocker, Watermark)
- Built on QPDF C++ library — fast and reliable
- Can open owner-password-protected PDFs without any password
- For user-password-protected PDFs, user must supply the password
- We CANNOT crack passwords — only remove owner restrictions
- Page overlay feature works perfectly for watermarking

### img2pdf (Image to PDF)
- Embeds images directly into PDF without re-encoding
- Preserves quality, produces smaller files than Pillow's PDF save
- Limitation: PNG alpha channels must be flattened first
- Only handles raster images (JPEG, PNG, TIFF)

### Pillow (Image operations)
- De-facto Python imaging library
- Handles compress, resize, format conversion
- JPEG quality parameter (1-95) controls compression
- WebP support built-in
- For very large images, consider pyvips (lower memory usage)

### pdf2image (PDF to Image)
- Requires poppler system dependency (apt-get install poppler-utils)
- Must be included in Docker image
- Memory-intensive for high-DPI rendering of large PDFs
- Alternative: pypdfium2 (no system deps, Apache-2.0)

### WeasyPrint (Markdown to PDF)
- Requires system dependencies: Pango, GDK-PixBuf, cairo
- Heavy install footprint (~200MB in Docker)
- Pipeline: Markdown → HTML (via `markdown` lib) → PDF (via WeasyPrint)
- Alternative: fpdf2 (lighter but less capable styling)

### qrcode (QR Generator)
- Requires Pillow for PNG output (SVG works without)
- Simple API: `qrcode.make(data)` returns image
- Customizable: colors, box size, border, error correction level

## System Dependencies (for Docker)

```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libcairo2 \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*
```

## CAPTCHA Options Evaluated

| Service | Free Tier | Recommendation |
|---------|-----------|----------------|
| Cloudflare Turnstile | Unlimited | ✅ CHOSEN — privacy-friendly, no puzzles |
| hCaptcha | Free (with branding) | Good alternative |
| Google reCAPTCHA | 1M assessments/month | Too invasive for a privacy-focused tool site |

## Cost Summary

| Item | Monthly Cost |
|------|-------------|
| Domain (cloudry.in) | Already owned |
| GitHub (private repo) | Free |
| Frontend hosting (GitHub Pages) | Free |
| Backend hosting (Render free tier) | Free |
| Cloudflare DNS + CDN | Free |
| SSL certificates | Free (auto) |
| Libraries | Free |
| CI/CD (GitHub Actions) | Free (2000 min/month) |
| **TOTAL** | **$0/month** |
