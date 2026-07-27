"""Tests for markdown service."""

from unittest.mock import MagicMock, patch

import pytest

from src.services.markdown_service import MarkdownService


def test_empty_content_raises_error():
    service = MarkdownService()
    with pytest.raises(ValueError, match="cannot be empty"):
        service.to_pdf("", "Test")


def test_whitespace_only_raises_error():
    service = MarkdownService()
    with pytest.raises(ValueError, match="cannot be empty"):
        service.to_pdf("   \n\t  ", "Test")


@patch("src.services.markdown_service.weasyprint", create=True)
def test_to_pdf_calls_weasyprint(mock_wp):
    """Test that the service correctly processes markdown and calls weasyprint."""
    # Mock weasyprint at the point of import inside the method
    mock_html = MagicMock()
    mock_wp.HTML.return_value = mock_html
    mock_html.write_pdf = MagicMock(side_effect=lambda buf: buf.write(b"%PDF-fake"))

    with patch.dict("sys.modules", {"weasyprint": mock_wp}):
        service = MarkdownService()
        result = service.to_pdf("# Hello\n\nWorld", "Test Doc")
        content = result.read()
        assert content == b"%PDF-fake"
