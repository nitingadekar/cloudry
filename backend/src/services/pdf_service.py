"""PDF processing service using pikepdf and pypdf."""

import io
import zipfile

import pikepdf
from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

from src.logging_config import get_logger

logger = get_logger("pdf_service")


class PDFService:
    """Handles all PDF-related operations."""

    def unlock(self, content: bytes, password: str = "") -> io.BytesIO:
        """Remove password restrictions from a PDF.

        Owner-password-only PDFs (restrictions on print/edit) can be opened without a password.
        User-password PDFs require the password to be provided.
        """
        try:
            pdf = pikepdf.open(io.BytesIO(content), password=password)
        except pikepdf.PasswordError:
            if password:
                raise ValueError("Incorrect password provided")
            raise ValueError("This PDF requires a password to open. Please provide the password.")

        output = io.BytesIO()
        pdf.save(output)
        pdf.close()
        output.seek(0)
        logger.info("PDF unlocked successfully")
        return output

    def merge(self, contents: list[bytes]) -> io.BytesIO:
        """Merge multiple PDFs into one."""
        if len(contents) < 2:
            raise ValueError("At least 2 PDF files are required for merging")

        writer = PdfWriter()
        for content in contents:
            reader = PdfReader(io.BytesIO(content))
            for page in reader.pages:
                writer.add_page(page)

        output = io.BytesIO()
        writer.write(output)
        output.seek(0)
        logger.info("Merged PDFs", extra={"file_count": len(contents)})
        return output

    def split(self, content: bytes, pages: str) -> io.BytesIO:
        """Split a PDF by extracting specified pages.

        Pages format: "1-3,5,7-9" — page numbers are 1-indexed.
        """
        reader = PdfReader(io.BytesIO(content))
        total_pages = len(reader.pages)
        page_indices = self._parse_page_ranges(pages, total_pages)

        writer = PdfWriter()
        for idx in page_indices:
            writer.add_page(reader.pages[idx])

        output = io.BytesIO()
        writer.write(output)
        output.seek(0)
        logger.info("PDF split", extra={"pages_extracted": len(page_indices)})
        return output

    def to_images(self, content: bytes, format: str = "png") -> io.BytesIO:
        """Convert PDF pages to images, returned as a ZIP file."""
        from pdf2image import convert_from_bytes

        format = format.lower()
        if format not in ("png", "jpg", "jpeg"):
            raise ValueError("Supported formats: png, jpg")

        pil_format = "JPEG" if format in ("jpg", "jpeg") else "PNG"
        images = convert_from_bytes(content, dpi=150)

        output = io.BytesIO()
        with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zf:
            for i, img in enumerate(images, 1):
                img_buffer = io.BytesIO()
                img.save(img_buffer, format=pil_format)
                ext = "jpg" if format in ("jpg", "jpeg") else "png"
                zf.writestr(f"page_{i}.{ext}", img_buffer.getvalue())

        output.seek(0)
        logger.info("PDF converted to images", extra={"pages": len(images), "format": format})
        return output

    def add_watermark(self, content: bytes, text: str) -> io.BytesIO:
        """Add a diagonal text watermark to every page of a PDF."""
        # Create watermark PDF
        watermark_buffer = io.BytesIO()
        c = canvas.Canvas(watermark_buffer, pagesize=letter)
        c.setFont("Helvetica", 50)
        c.setFillAlpha(0.3)
        c.setFillColorRGB(0.5, 0.5, 0.5)
        c.saveState()
        c.translate(letter[0] / 2, letter[1] / 2)
        c.rotate(45)
        c.drawCentredString(0, 0, text)
        c.restoreState()
        c.save()
        watermark_buffer.seek(0)

        # Overlay watermark on each page
        watermark_pdf = pikepdf.open(watermark_buffer)
        watermark_page = watermark_pdf.pages[0]

        pdf = pikepdf.open(io.BytesIO(content))
        for page in pdf.pages:
            page.add_overlay(watermark_page)

        output = io.BytesIO()
        pdf.save(output)
        pdf.close()
        watermark_pdf.close()
        output.seek(0)
        logger.info("Watermark added", extra={"text": text})
        return output

    @staticmethod
    def _parse_page_ranges(pages: str, total_pages: int) -> list[int]:
        """Parse page range string into 0-indexed page numbers.

        Input: "1-3,5,7-9" (1-indexed)
        Output: [0, 1, 2, 4, 6, 7, 8] (0-indexed)
        """
        indices = []
        for part in pages.split(","):
            part = part.strip()
            if "-" in part:
                start, end = part.split("-", 1)
                start_idx = int(start) - 1
                end_idx = int(end) - 1
                if start_idx < 0 or end_idx >= total_pages:
                    raise ValueError(f"Page range {part} is out of bounds (total pages: {total_pages})")
                indices.extend(range(start_idx, end_idx + 1))
            else:
                idx = int(part) - 1
                if idx < 0 or idx >= total_pages:
                    raise ValueError(f"Page {part} is out of bounds (total pages: {total_pages})")
                indices.append(idx)
        return sorted(set(indices))
