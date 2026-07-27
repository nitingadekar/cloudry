"""Tests for QR code generation service."""

import pytest

from src.services.qr_service import QRService


def test_generate_png():
    service = QRService()
    result, media_type = service.generate("https://cloudry.in", format="png")
    assert media_type == "image/png"
    content = result.read()
    assert len(content) > 0
    # PNG magic bytes
    assert content[:8] == b"\x89PNG\r\n\x1a\n"


def test_generate_svg():
    service = QRService()
    result, media_type = service.generate("Hello World", format="svg")
    assert media_type == "image/svg+xml"
    content = result.read()
    assert b"<svg" in content or b"<?xml" in content


def test_generate_empty_data():
    service = QRService()
    with pytest.raises(ValueError, match="Data cannot be empty"):
        service.generate("")


def test_generate_invalid_size():
    service = QRService()
    with pytest.raises(ValueError, match="Size must be between"):
        service.generate("test", size=0)
    with pytest.raises(ValueError, match="Size must be between"):
        service.generate("test", size=51)


def test_generate_qr_endpoint(test_client):
    resp = test_client.post(
        "/api/v1/qr/generate",
        data={"data": "https://cloudry.in", "format": "png", "size": "10"},
    )
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "image/png"
    assert "qrcode.png" in resp.headers["content-disposition"]


def test_generate_qr_svg_endpoint(test_client):
    resp = test_client.post(
        "/api/v1/qr/generate",
        data={"data": "test data", "format": "svg"},
    )
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "image/svg+xml"
