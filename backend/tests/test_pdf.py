"""Tests for PDF service."""

import io

import pikepdf
import pytest
from pypdf import PdfWriter

from src.services.pdf_service import InvalidPDFError, PDFService


def _create_test_pdf(num_pages: int = 3) -> bytes:
    """Create a simple test PDF with blank pages."""
    writer = PdfWriter()
    for _ in range(num_pages):
        writer.add_blank_page(width=612, height=792)
    buffer = io.BytesIO()
    writer.write(buffer)
    buffer.seek(0)
    return buffer.getvalue()


def _create_encrypted_pdf(password: str = "secret") -> bytes:  # noqa: S107
    """Create a password-protected test PDF."""
    buffer = io.BytesIO()
    pdf = pikepdf.new()
    pdf.add_blank_page(page_size=(612, 792))
    pdf.save(buffer, encryption=pikepdf.Encryption(owner=password, user=password))
    buffer.seek(0)
    return buffer.getvalue()


# --- PDF Validation Tests ---


class TestValidatePDF:
    """Tests for the validate_pdf static method."""

    def test_validate_valid_pdf(self):
        service = PDFService()
        content = _create_test_pdf()
        # Should not raise
        service.validate_pdf(content)

    def test_validate_empty_content(self):
        service = PDFService()
        with pytest.raises(InvalidPDFError, match="empty or too small"):
            service.validate_pdf(b"")

    def test_validate_too_small(self):
        service = PDFService()
        with pytest.raises(InvalidPDFError, match="empty or too small"):
            service.validate_pdf(b"tiny")

    def test_validate_not_pdf(self):
        service = PDFService()
        with pytest.raises(InvalidPDFError, match="not a valid PDF"):
            service.validate_pdf(b"This is a plain text file, not a PDF at all.")

    def test_validate_random_bytes(self):
        service = PDFService()
        import os
        with pytest.raises(InvalidPDFError):
            service.validate_pdf(os.urandom(1024))

    def test_validate_encrypted_pdf(self):
        service = PDFService()
        content = _create_encrypted_pdf()
        with pytest.raises(InvalidPDFError, match="password-protected"):
            service.validate_pdf(content)

    def test_validate_corrupt_pdf(self):
        """A file that starts with %PDF- but has garbage content."""
        service = PDFService()
        corrupt = b"%PDF-1.4\nthis is not valid pdf structure at all"
        with pytest.raises(InvalidPDFError):
            service.validate_pdf(corrupt)


# --- Service Method Tests with Invalid Input ---


class TestMergeValidation:
    def test_merge_with_non_pdf_file(self):
        service = PDFService()
        valid_pdf = _create_test_pdf(1)
        invalid = b"not a pdf file content here"
        with pytest.raises(InvalidPDFError, match="File 2"):
            service.merge([valid_pdf, invalid])

    def test_merge_with_encrypted_pdf(self):
        service = PDFService()
        valid_pdf = _create_test_pdf(1)
        encrypted = _create_encrypted_pdf()
        with pytest.raises(InvalidPDFError, match="password-protected"):
            service.merge([valid_pdf, encrypted])


class TestSplitValidation:
    def test_split_with_non_pdf(self):
        service = PDFService()
        with pytest.raises(InvalidPDFError, match="not a valid PDF"):
            service.split(b"hello world this is not a pdf", "1-2")

    def test_split_with_encrypted_pdf(self):
        service = PDFService()
        content = _create_encrypted_pdf()
        with pytest.raises(InvalidPDFError, match="password-protected"):
            service.split(content, "1")


class TestWatermarkValidation:
    def test_watermark_with_non_pdf(self):
        service = PDFService()
        with pytest.raises(InvalidPDFError, match="not a valid PDF"):
            service.add_watermark(b"some random text content", "DRAFT")


class TestCompressValidation:
    def test_compress_with_non_pdf(self):
        service = PDFService()
        with pytest.raises(InvalidPDFError, match="not a valid PDF"):
            service.compress(b"definitely not a pdf file here")


# --- Endpoint Tests with Invalid Input ---


class TestPDFEndpointsValidation:
    def test_merge_endpoint_with_invalid_file(self, test_client):
        valid_pdf = _create_test_pdf(1)
        invalid = b"not a pdf"
        resp = test_client.post(
            "/api/v1/pdf/merge",
            files=[
                ("files", ("file1.pdf", valid_pdf, "application/pdf")),
                ("files", ("file2.pdf", invalid, "application/pdf")),
            ],
        )
        assert resp.status_code == 422
        assert "not a valid PDF" in resp.json()["detail"]

    def test_split_endpoint_with_invalid_file(self, test_client):
        resp = test_client.post(
            "/api/v1/pdf/split",
            files={"file": ("test.pdf", b"not a pdf at all", "application/pdf")},
            data={"pages": "1-3"},
        )
        assert resp.status_code == 422
        assert "not a valid PDF" in resp.json()["detail"]

    def test_compress_endpoint_with_invalid_file(self, test_client):
        resp = test_client.post(
            "/api/v1/pdf/compress",
            files={"file": ("test.pdf", b"garbage content", "application/pdf")},
        )
        assert resp.status_code == 422
        assert "not a valid PDF" in resp.json()["detail"]

    def test_watermark_endpoint_with_invalid_file(self, test_client):
        resp = test_client.post(
            "/api/v1/pdf/watermark",
            files={"file": ("test.pdf", b"not pdf data", "application/pdf")},
            data={"text": "DRAFT"},
        )
        assert resp.status_code == 422
        assert "not a valid PDF" in resp.json()["detail"]

    def test_merge_endpoint_with_encrypted_file(self, test_client):
        valid_pdf = _create_test_pdf(1)
        encrypted = _create_encrypted_pdf()
        resp = test_client.post(
            "/api/v1/pdf/merge",
            files=[
                ("files", ("file1.pdf", valid_pdf, "application/pdf")),
                ("files", ("file2.pdf", encrypted, "application/pdf")),
            ],
        )
        assert resp.status_code == 422
        assert "password-protected" in resp.json()["detail"]

    def test_unlock_endpoint_with_wrong_password(self, test_client):
        encrypted = _create_encrypted_pdf("mypassword")
        resp = test_client.post(
            "/api/v1/pdf/unlock",
            files={"file": ("locked.pdf", encrypted, "application/pdf")},
            data={"password": "wrongpassword"},
        )
        assert resp.status_code == 422
        assert "Incorrect password" in resp.json()["detail"]


# --- Original Tests (existing behavior still works) ---


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
