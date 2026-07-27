"""QR code tool endpoints."""

from fastapi import APIRouter, Depends, Form
from fastapi.responses import StreamingResponse

from src.middleware.captcha import verify_turnstile
from src.services.qr_service import QRService

router = APIRouter()
qr_service = QRService()


@router.post("/generate", dependencies=[Depends(verify_turnstile)])
async def generate_qr(
    data: str = Form(...),
    format: str = Form(default="png"),
    size: int = Form(default=10),
    error_correction: str = Form(default="M"),
):
    """Generate a QR code from text or URL.

    Args:
        data: The text/URL to encode in the QR code.
        format: Output format — "png" or "svg".
        size: Box size in pixels (1-50). Default: 10.
        error_correction: L (7%), M (15%), Q (25%), H (30%). Default: M.
    """
    result, media_type = qr_service.generate(data, format, size, error_correction)
    ext = "svg" if format == "svg" else "png"
    return StreamingResponse(
        result,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename=qrcode.{ext}"},
    )
