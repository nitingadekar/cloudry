"""Image processing service using Pillow and img2pdf."""

import io

import img2pdf
from PIL import Image

from src.logging_config import get_logger

logger = get_logger("image_service")

# Mapping of format names to Pillow format strings and MIME types
FORMAT_MAP = {
    "png": ("PNG", "image/png", "png"),
    "jpg": ("JPEG", "image/jpeg", "jpg"),
    "jpeg": ("JPEG", "image/jpeg", "jpg"),
    "webp": ("WEBP", "image/webp", "webp"),
    "bmp": ("BMP", "image/bmp", "bmp"),
    "gif": ("GIF", "image/gif", "gif"),
}


class ImageService:
    """Handles all image-related operations."""

    def to_pdf(self, contents: list[bytes]) -> io.BytesIO:
        """Convert one or more images to a single PDF.

        Uses img2pdf for lossless conversion (no re-encoding).
        Falls back to Pillow for formats img2pdf doesn't support (e.g., PNG with alpha).
        """
        # Try img2pdf first (lossless, smaller output)
        try:
            pdf_bytes = img2pdf.convert(contents)
            output = io.BytesIO(pdf_bytes)
            output.seek(0)
            logger.info("Images converted to PDF via img2pdf", extra={"image_count": len(contents)})
            return output
        except Exception:
            # Fallback to Pillow (handles alpha channels, exotic formats)
            pass

        images = []
        for content in contents:
            img = Image.open(io.BytesIO(content))
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            images.append(img)

        output = io.BytesIO()
        if len(images) == 1:
            images[0].save(output, format="PDF")
        else:
            images[0].save(output, format="PDF", save_all=True, append_images=images[1:])

        output.seek(0)
        logger.info("Images converted to PDF via Pillow", extra={"image_count": len(images)})
        return output

    def compress(self, content: bytes, filename: str, quality: int = 75) -> tuple[io.BytesIO, str]:
        """Compress an image to reduce file size.

        Returns (output_buffer, media_type).
        """
        quality = max(1, min(95, quality))

        img = Image.open(io.BytesIO(content))
        original_format = img.format or "JPEG"

        # Convert RGBA to RGB for JPEG compression
        if img.mode in ("RGBA", "P") and original_format == "JPEG":
            img = img.convert("RGB")

        output = io.BytesIO()
        if original_format in ("JPEG", "JPG"):
            img.save(output, format="JPEG", quality=quality, optimize=True)
            media_type = "image/jpeg"
        elif original_format == "PNG":
            img.save(output, format="PNG", optimize=True)
            media_type = "image/png"
        elif original_format == "WEBP":
            img.save(output, format="WEBP", quality=quality)
            media_type = "image/webp"
        else:
            img.save(output, format="JPEG", quality=quality, optimize=True)
            media_type = "image/jpeg"

        output.seek(0)
        logger.info(
            "Image compressed",
            extra={"original_size": len(content), "compressed_size": output.getbuffer().nbytes, "quality": quality},
        )
        return output, media_type

    def resize(self, content: bytes, filename: str, width: int, height: int) -> tuple[io.BytesIO, str]:
        """Resize an image to specified dimensions."""
        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive integers")
        if width > 10000 or height > 10000:
            raise ValueError("Maximum dimension is 10000 pixels")

        img = Image.open(io.BytesIO(content))
        original_format = img.format or "PNG"
        img_resized = img.resize((width, height), Image.Resampling.LANCZOS)

        output = io.BytesIO()
        pil_format = original_format if original_format in ("PNG", "JPEG", "WEBP", "GIF") else "PNG"

        if pil_format == "JPEG" and img_resized.mode in ("RGBA", "P"):
            img_resized = img_resized.convert("RGB")

        img_resized.save(output, format=pil_format)
        media_type = FORMAT_MAP.get(pil_format.lower(), ("PNG", "image/png", "png"))[1]

        output.seek(0)
        logger.info("Image resized", extra={"width": width, "height": height})
        return output, media_type

    def convert_format(self, content: bytes, target_format: str) -> tuple[io.BytesIO, str, str]:
        """Convert image to a different format.

        Returns (output_buffer, media_type, file_extension).
        """
        target_format = target_format.lower().strip()
        if target_format not in FORMAT_MAP:
            raise ValueError(f"Unsupported format: {target_format}. Supported: {', '.join(FORMAT_MAP.keys())}")

        pil_format, media_type, ext = FORMAT_MAP[target_format]

        img = Image.open(io.BytesIO(content))
        if pil_format == "JPEG" and img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        output = io.BytesIO()
        img.save(output, format=pil_format)
        output.seek(0)

        logger.info("Image format converted", extra={"target_format": target_format})
        return output, media_type, ext
