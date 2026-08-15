"""Tests for caption generator service and endpoints."""

import io
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image

from src.services.caption_service import CaptionService


def _create_test_image(width: int = 200, height: int = 200, format: str = "JPEG") -> bytes:
    """Create a simple test image."""
    img = Image.new("RGB", (width, height), color=(100, 150, 200))
    buffer = io.BytesIO()
    img.save(buffer, format=format)
    buffer.seek(0)
    return buffer.getvalue()


def _create_large_test_image() -> bytes:
    """Create a test image larger than 1024px to test resizing."""
    img = Image.new("RGB", (2000, 1500), color=(200, 100, 50))
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG")
    buffer.seek(0)
    return buffer.getvalue()


def _create_rgba_image() -> bytes:
    """Create a RGBA PNG image to test alpha channel handling."""
    img = Image.new("RGBA", (100, 100), color=(100, 150, 200, 128))
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer.getvalue()


class TestCaptionServiceHelpers:
    """Tests for helper methods."""

    def test_get_themes_returns_list(self):
        themes = CaptionService.get_themes()
        assert isinstance(themes, list)
        assert len(themes) > 10
        assert "romantic" in themes
        assert "badass" in themes
        assert "catchy" in themes

    def test_get_languages_returns_list(self):
        languages = CaptionService.get_languages()
        assert isinstance(languages, list)
        assert "English" in languages
        assert "Hindi" in languages
        assert "Marathi" in languages

    def test_prepare_image_resizes_large_image(self):
        service = CaptionService()
        content = _create_large_test_image()
        base64_str = service._prepare_image(content)
        assert isinstance(base64_str, str)
        assert len(base64_str) > 0

    def test_prepare_image_handles_rgba(self):
        service = CaptionService()
        content = _create_rgba_image()
        base64_str = service._prepare_image(content)
        assert isinstance(base64_str, str)
        assert len(base64_str) > 0

    def test_prepare_image_small_image_not_resized(self):
        service = CaptionService()
        content = _create_test_image(100, 100)
        base64_str = service._prepare_image(content)
        assert isinstance(base64_str, str)

    def test_build_prompt_contains_theme(self):
        service = CaptionService()
        prompt = service._build_prompt("romantic", "English", 3)
        assert "romantic" in prompt
        assert "3" in prompt

    def test_build_prompt_non_english_includes_language(self):
        service = CaptionService()
        prompt = service._build_prompt("funny", "Hindi", 3)
        assert "Hindi" in prompt
        assert "native script" in prompt.lower() or "Hindi script" in prompt

    def test_parse_response_standard_format(self):
        service = CaptionService()
        raw = '{"captions": ["Chasing sunsets and losing track of time 🌅", "The sky painted itself just for us tonight ✨", "Golden hour never looked this good 🔥"]}'
        result = service._parse_response(raw, "aesthetic", "English")
        assert len(result["captions"]) == 3
        assert "🌅" in result["captions"][0]
        assert result["theme"] == "aesthetic"
        assert result["language"] == "English"

    def test_parse_response_fallback_on_bad_format(self):
        service = CaptionService()
        raw = "Just some random text without proper format"
        result = service._parse_response(raw, "catchy", "English")
        # Should fallback to using the whole response
        assert len(result["captions"]) == 1
        assert result["captions"][0] == raw.strip()

    def test_parse_response_with_markdown_fences(self):
        service = CaptionService()
        raw = '```json\n{"captions": ["Caption one 🎉", "Caption two ✨", "Caption three 🔥"]}\n```'
        result = service._parse_response(raw, "funny", "English")
        assert len(result["captions"]) == 3

    def test_parse_response_partial_format(self):
        service = CaptionService()
        raw = '{"captions": ["Living my best nine lives 🐱"]}'
        result = service._parse_response(raw, "funny", "English")
        assert len(result["captions"]) == 1


class TestCaptionServiceValidation:
    """Tests for input validation."""

    def test_invalid_theme_raises(self):
        service = CaptionService()
        service._client = MagicMock()  # Set internal client directly to avoid API call
        with pytest.raises(ValueError, match="Invalid theme"):
            service.generate_captions(_create_test_image(), theme="invalid_theme")

    def test_invalid_language_raises(self):
        service = CaptionService()
        service._client = MagicMock()  # Set internal client directly to avoid API call
        with pytest.raises(ValueError, match="Invalid language"):
            service.generate_captions(_create_test_image(), language="Klingon")

    def test_missing_api_key_raises(self):
        service = CaptionService()
        with patch("src.services.caption_service.settings") as mock_settings:
            mock_settings.groq_api_key = ""
            service._client = None
            with pytest.raises(ValueError, match="GROQ_API_KEY"):
                _ = service.client


class TestCaptionServiceGeneration:
    """Tests for caption generation with mocked Groq API."""

    @patch("src.services.caption_service.Groq")
    def test_generate_captions_success(self, mock_groq_class):
        # Mock the Groq client
        mock_client = MagicMock()
        mock_groq_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"captions": ["On top of the world 🏔️", "Mountains calling and I must go ⛰️", "Higher than my expectations 🚀"]}'
        mock_client.chat.completions.create.return_value = mock_response

        service = CaptionService()
        service._client = mock_client

        result = service.generate_captions(
            _create_test_image(),
            theme="travel",
            language="English",
            count=3,
        )

        assert len(result["captions"]) == 3
        assert result["theme"] == "travel"
        assert result["language"] == "English"
        assert "description" not in result
        mock_client.chat.completions.create.assert_called_once()

    @patch("src.services.caption_service.Groq")
    def test_generate_captions_clamps_count(self, mock_groq_class):
        mock_client = MagicMock()
        mock_groq_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "DESCRIPTION: test\nCAPTION 1: hello"
        mock_client.chat.completions.create.return_value = mock_response

        service = CaptionService()
        service._client = mock_client

        # Count should be clamped to 2-5
        service.generate_captions(_create_test_image(), count=10)
        service.generate_captions(_create_test_image(), count=0)

        # Should not raise


class TestCaptionEndpoints:
    """Tests for caption router endpoints."""

    def test_get_themes_endpoint(self, test_client):
        resp = test_client.get("/api/v1/caption/themes")
        assert resp.status_code == 200
        data = resp.json()
        assert "themes" in data
        assert "romantic" in data["themes"]

    def test_get_languages_endpoint(self, test_client):
        resp = test_client.get("/api/v1/caption/languages")
        assert resp.status_code == 200
        data = resp.json()
        assert "languages" in data
        assert "English" in data["languages"]
        assert "Hindi" in data["languages"]

    def test_generate_rejects_non_image(self, test_client):
        resp = test_client.post(
            "/api/v1/caption/generate",
            files={"file": ("test.txt", b"hello world", "text/plain")},
            data={"theme": "catchy"},
        )
        assert resp.status_code == 422
        assert "valid image" in resp.json()["detail"]

    def test_generate_rejects_empty_file(self, test_client):
        resp = test_client.post(
            "/api/v1/caption/generate",
            files={"file": ("test.jpg", b"x" * 50, "image/jpeg")},
            data={"theme": "catchy"},
        )
        assert resp.status_code == 422
        assert "empty or invalid" in resp.json()["detail"]

    def test_generate_rejects_invalid_theme(self, test_client):
        content = _create_test_image()
        resp = test_client.post(
            "/api/v1/caption/generate",
            files={"file": ("test.jpg", content, "image/jpeg")},
            data={"theme": "nonexistent_theme"},
        )
        assert resp.status_code == 422
        assert "Invalid theme" in resp.json()["detail"]

    def test_generate_graceful_when_api_key_missing(self, test_client):
        """When GROQ_API_KEY is not configured, endpoint should return 503 not 500."""
        content = _create_test_image()
        with patch("src.routers.caption.caption_service") as mock_service:
            mock_service.generate_captions.side_effect = ValueError("GROQ_API_KEY is not configured")
            resp = test_client.post(
                "/api/v1/caption/generate",
                files={"file": ("test.jpg", content, "image/jpeg")},
                data={"theme": "catchy", "language": "English"},
            )
        # ValueError with "api_key" in message should be caught and return 422
        assert resp.status_code == 422
        assert "GROQ_API_KEY" in resp.json()["detail"]

    def test_generate_returns_503_on_auth_error(self, test_client):
        """When Groq API rejects the key, return 503 service unavailable."""
        content = _create_test_image()
        with patch("src.routers.caption.caption_service") as mock_service:
            mock_service.generate_captions.side_effect = Exception("authentication failed: invalid api_key")
            resp = test_client.post(
                "/api/v1/caption/generate",
                files={"file": ("test.jpg", content, "image/jpeg")},
                data={"theme": "catchy", "language": "English"},
            )
        assert resp.status_code == 503
        assert "temporarily unavailable" in resp.json()["detail"]

    def test_generate_returns_429_on_rate_limit(self, test_client):
        """When Groq rate limits us, return 429."""
        content = _create_test_image()
        with patch("src.routers.caption.caption_service") as mock_service:
            mock_service.generate_captions.side_effect = Exception("rate_limit_exceeded")
            resp = test_client.post(
                "/api/v1/caption/generate",
                files={"file": ("test.jpg", content, "image/jpeg")},
                data={"theme": "catchy", "language": "English"},
            )
        assert resp.status_code == 429
        assert "Too many requests" in resp.json()["detail"]

    @patch("src.routers.caption.caption_service")
    def test_generate_success(self, mock_service, test_client):
        mock_service.generate_captions.return_value = {
            "captions": ["Caption 1 ✨", "Caption 2 🔥", "Caption 3 💫"],
            "theme": "catchy",
            "language": "English",
        }

        content = _create_test_image()
        resp = test_client.post(
            "/api/v1/caption/generate",
            files={"file": ("test.jpg", content, "image/jpeg")},
            data={"theme": "catchy", "language": "English"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["captions"]) == 3
        assert data["theme"] == "catchy"
        assert "description" not in data
