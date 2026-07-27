"""Tests for image processing service."""

import io

from PIL import Image

from src.services.image_service import ImageService


def _create_test_image(format: str = "PNG", size: tuple = (100, 100), mode: str = "RGB") -> bytes:
    """Create a test image and return as bytes."""
    img = Image.new(mode, size, color="red")
    buffer = io.BytesIO()
    img.save(buffer, format=format)
    buffer.seek(0)
    return buffer.getvalue()


def test_compress_jpeg():
    service = ImageService()
    content = _create_test_image("JPEG")
    result, media_type = service.compress(content, "test.jpg", quality=50)
    assert media_type == "image/jpeg"
    assert result.read()


def test_compress_png():
    service = ImageService()
    content = _create_test_image("PNG")
    result, media_type = service.compress(content, "test.png", quality=75)
    assert media_type == "image/png"
    assert result.read()


def test_resize():
    service = ImageService()
    content = _create_test_image("PNG", size=(200, 200))
    result, media_type = service.resize(content, "test.png", 50, 50)

    # Verify dimensions
    img = Image.open(result)
    assert img.size == (50, 50)


def test_resize_invalid_dimensions():
    service = ImageService()
    content = _create_test_image("PNG")
    try:
        service.resize(content, "test.png", 0, 100)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


def test_convert_png_to_jpg():
    service = ImageService()
    content = _create_test_image("PNG")
    result, media_type, ext = service.convert_format(content, "jpg")
    assert media_type == "image/jpeg"
    assert ext == "jpg"
    # Verify it's a valid JPEG
    img = Image.open(result)
    assert img.format == "JPEG"


def test_convert_jpg_to_webp():
    service = ImageService()
    content = _create_test_image("JPEG")
    result, media_type, ext = service.convert_format(content, "webp")
    assert media_type == "image/webp"
    assert ext == "webp"


def test_convert_invalid_format():
    service = ImageService()
    content = _create_test_image("PNG")
    try:
        service.convert_format(content, "tiff")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


def test_to_pdf():
    service = ImageService()
    img1 = _create_test_image("JPEG")
    img2 = _create_test_image("JPEG")
    result = service.to_pdf([img1, img2])
    content = result.read()
    # PDF magic bytes
    assert content[:5] == b"%PDF-"


def test_image_compress_endpoint(test_client):
    content = _create_test_image("JPEG")
    resp = test_client.post(
        "/api/v1/image/compress",
        files={"file": ("test.jpg", content, "image/jpeg")},
        data={"quality": "50"},
    )
    assert resp.status_code == 200
    assert "image/" in resp.headers["content-type"]


def test_image_convert_endpoint(test_client):
    content = _create_test_image("PNG")
    resp = test_client.post(
        "/api/v1/image/convert",
        files={"file": ("test.png", content, "image/png")},
        data={"target_format": "jpg"},
    )
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "image/jpeg"
