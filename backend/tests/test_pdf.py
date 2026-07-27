"""Tests for PDF service."""

import io

import pytest
from pypdf import PdfWriter

from src.services.pdf_service import PDFService


def _create_test_pdf(num_pages: int = 3) -> bytes:
    """Create a simple test PDF with blank pages."""
    writer = PdfWriter()
    for _ in range(num_pages):
        writer.add_blank_page(width=612, height=792)
    buffer = io.BytesIO()
    writer.write(buffer)
    buffer.seek(0)
    return buffer.getvalue()


def test_unlock_unrestricted_pdf():
    service = PDFService()
    content = _create_test_pdf()
    result = service.unlock(content)
    assert result.read()[:5] == b"%PDF-"


def test_merge_two_pdfs():
    service = PDFService()
    pdf1 = _create_test_pdf(2)
    pdf2 = _create_test_pdf(3)
    result = service.merge([pdf1, pdf2])
    # Verify it's a valid PDF
    assert result.read()[:5] == b"%PDF-"


def test_merge_requires_two_files():
    service = PDFService()
    with pytest.raises(ValueError, match="At least 2"):
        service.merge([_create_test_pdf()])


def test_split_extract_pages():
    service = PDFService()
    content = _create_test_pdf(5)
    result = service.split(content, "1-3")
    assert result.read()[:5] == b"%PDF-"


def test_split_single_page():
    service = PDFService()
    content = _create_test_pdf(5)
    result = service.split(content, "2")
    assert result.read()[:5] == b"%PDF-"


def test_split_comma_separated():
    service = PDFService()
    content = _create_test_pdf(5)
    result = service.split(content, "1,3,5")
    assert result.read()[:5] == b"%PDF-"


def test_split_out_of_bounds():
    service = PDFService()
    content = _create_test_pdf(3)
    with pytest.raises(ValueError, match="out of bounds"):
        service.split(content, "1-5")


def test_parse_page_ranges():
    indices = PDFService._parse_page_ranges("1-3,5,7-9", 10)
    assert indices == [0, 1, 2, 4, 6, 7, 8]


def test_parse_page_ranges_single():
    indices = PDFService._parse_page_ranges("3", 5)
    assert indices == [2]


def test_watermark():
    service = PDFService()
    content = _create_test_pdf(2)
    result = service.add_watermark(content, "CONFIDENTIAL")
    assert result.read()[:5] == b"%PDF-"


def test_compress():
    service = PDFService()
    content = _create_test_pdf(3)
    result = service.compress(content)
    compressed = result.read()
    assert compressed[:5] == b"%PDF-"


def test_pdf_merge_endpoint(test_client):
    pdf1 = _create_test_pdf(1)
    pdf2 = _create_test_pdf(1)
    resp = test_client.post(
        "/api/v1/pdf/merge",
        files=[
            ("files", ("file1.pdf", pdf1, "application/pdf")),
            ("files", ("file2.pdf", pdf2, "application/pdf")),
        ],
    )
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"


def test_pdf_split_endpoint(test_client):
    content = _create_test_pdf(5)
    resp = test_client.post(
        "/api/v1/pdf/split",
        files={"file": ("test.pdf", content, "application/pdf")},
        data={"pages": "1-3"},
    )
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"


def test_pdf_compress_endpoint(test_client):
    content = _create_test_pdf(2)
    resp = test_client.post(
        "/api/v1/pdf/compress",
        files={"file": ("test.pdf", content, "application/pdf")},
    )
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"


def test_pdf_unlock_endpoint(test_client):
    content = _create_test_pdf(1)
    resp = test_client.post(
        "/api/v1/pdf/unlock",
        files={"file": ("test.pdf", content, "application/pdf")},
    )
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"


def test_pdf_watermark_endpoint(test_client):
    content = _create_test_pdf(1)
    resp = test_client.post(
        "/api/v1/pdf/watermark",
        files={"file": ("test.pdf", content, "application/pdf")},
        data={"text": "DRAFT"},
    )
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
