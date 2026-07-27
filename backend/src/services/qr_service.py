"""QR code generation service."""

import io

import qrcode
import qrcode.constants
from qrcode.image.svg import SvgImage

from src.logging_config import get_logger

logger = get_logger("qr_service")

ERROR_CORRECTION_MAP = {
    "L": qrcode.constants.ERROR_CORRECT_L,
    "M": qrcode.constants.ERROR_CORRECT_M,
    "Q": qrcode.constants.ERROR_CORRECT_Q,
    "H": qrcode.constants.ERROR_CORRECT_H,
}


class QRService:
    """Handles QR code generation."""

    def generate(
        self, data: str, format: str = "png", size: int = 10, error_correction: str = "M"
    ) -> tuple[io.BytesIO, str]:
        """Generate a QR code from text/URL.

        Returns (output_buffer, media_type).
        """
        if not data:
            raise ValueError("Data cannot be empty")
        if size < 1 or size > 50:
            raise ValueError("Size must be between 1 and 50")

        ec_level = ERROR_CORRECTION_MAP.get(error_correction.upper(), qrcode.constants.ERROR_CORRECT_M)

        qr = qrcode.QRCode(
            version=None,  # Auto-determine version
            error_correction=ec_level,
            box_size=size,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        output = io.BytesIO()

        if format.lower() == "svg":
            img = qr.make_image(image_factory=SvgImage)
            img.save(output)
            media_type = "image/svg+xml"
        else:
            img = qr.make_image(fill_color="black", back_color="white")
            img.save(output, format="PNG")
            media_type = "image/png"

        output.seek(0)
        logger.info("QR code generated", extra={"format": format, "data_length": len(data)})
        return output, media_type
