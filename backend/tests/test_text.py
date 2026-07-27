"""Tests for text utility service (Base64, JSON, Color)."""

import pytest

from src.services.text_service import TextService

# ── Base64 Tests ──────────────────────────────────────────────────────────────


def test_base64_encode():
    service = TextService()
    result = service.base64_encode(b"Hello, World!")
    assert result == "SGVsbG8sIFdvcmxkIQ=="


def test_base64_encode_empty():
    service = TextService()
    result = service.base64_encode(b"")
    assert result == ""


def test_base64_decode():
    service = TextService()
    result = service.base64_decode("SGVsbG8sIFdvcmxkIQ==")
    assert result == b"Hello, World!"


def test_base64_decode_invalid():
    service = TextService()
    with pytest.raises(ValueError, match="Invalid base64"):
        service.base64_decode("not-valid-base64!!!")


def test_base64_roundtrip():
    service = TextService()
    original = b"Testing roundtrip 123!"
    encoded = service.base64_encode(original)
    decoded = service.base64_decode(encoded)
    assert decoded == original


# ── JSON Tests ────────────────────────────────────────────────────────────────


def test_json_format_valid():
    service = TextService()
    result = service.json_format('{"name":"Nitin","age":30}')
    assert '"name": "Nitin"' in result
    assert '"age": 30' in result
    assert "\n" in result  # Pretty-printed


def test_json_format_invalid():
    service = TextService()
    with pytest.raises(ValueError, match="Invalid JSON"):
        service.json_format("{invalid json}")


def test_json_validate_valid():
    service = TextService()
    result = service.json_validate('{"key": "value"}')
    assert result["valid"] is True
    assert result["error"] is None


def test_json_validate_invalid():
    service = TextService()
    result = service.json_validate("not json at all")
    assert result["valid"] is False
    assert result["error"] is not None


def test_json_validate_array():
    service = TextService()
    result = service.json_validate("[1, 2, 3]")
    assert result["valid"] is True


# ── Color Tests ───────────────────────────────────────────────────────────────


def test_color_hex_to_rgb():
    service = TextService()
    result = service.color_convert("#ff5733", "rgb")
    assert result["output"] == "rgb(255, 87, 51)"


def test_color_hex_no_hash_to_rgb():
    service = TextService()
    result = service.color_convert("ff5733", "rgb")
    assert result["output"] == "rgb(255, 87, 51)"


def test_color_rgb_to_hex():
    service = TextService()
    result = service.color_convert("255,87,51", "hex")
    assert result["output"] == "#ff5733"


def test_color_rgb_format_to_hex():
    service = TextService()
    result = service.color_convert("rgb(255, 87, 51)", "hex")
    assert result["output"] == "#ff5733"


def test_color_hex_to_hsl():
    service = TextService()
    result = service.color_convert("#ff0000", "hsl")
    assert "hsl(0" in result["output"]


def test_color_black():
    service = TextService()
    result = service.color_convert("#000000", "rgb")
    assert result["output"] == "rgb(0, 0, 0)"


def test_color_white():
    service = TextService()
    result = service.color_convert("#ffffff", "rgb")
    assert result["output"] == "rgb(255, 255, 255)"


def test_color_invalid():
    service = TextService()
    with pytest.raises(ValueError, match="Cannot parse color"):
        service.color_convert("not-a-color", "hex")


def test_color_invalid_target_format():
    service = TextService()
    with pytest.raises(ValueError, match="Unsupported target format"):
        service.color_convert("#ff5733", "cmyk")


# ── Endpoint Tests ────────────────────────────────────────────────────────────


def test_base64_encode_endpoint(test_client):
    resp = test_client.post(
        "/api/v1/text/base64/encode",
        data={"text": "Hello, World!"},
    )
    assert resp.status_code == 200
    assert resp.json()["encoded"] == "SGVsbG8sIFdvcmxkIQ=="


def test_base64_decode_endpoint(test_client):
    resp = test_client.post(
        "/api/v1/text/base64/decode",
        data={"encoded": "SGVsbG8sIFdvcmxkIQ=="},
    )
    assert resp.status_code == 200
    assert resp.json()["decoded"] == "Hello, World!"


def test_json_format_endpoint(test_client):
    resp = test_client.post(
        "/api/v1/text/json/format",
        data={"content": '{"a":1}'},
    )
    assert resp.status_code == 200
    assert '"a": 1' in resp.json()["formatted"]


def test_json_validate_endpoint(test_client):
    resp = test_client.post(
        "/api/v1/text/json/validate",
        data={"content": '{"valid": true}'},
    )
    assert resp.status_code == 200
    assert resp.json()["valid"] is True


def test_color_convert_endpoint(test_client):
    resp = test_client.post(
        "/api/v1/text/color/convert",
        data={"color": "#ff5733", "to_format": "rgb"},
    )
    assert resp.status_code == 200
    assert resp.json()["output"] == "rgb(255, 87, 51)"
