"""Tests for diff checker service and endpoint."""

from src.services.text_service import TextService


class TestDiffService:
    """Tests for TextService.diff_texts method."""

    def test_identical_texts(self):
        service = TextService()
        result = service.diff_texts("hello world", "hello world")
        assert result["identical"] is True
        assert result["stats"]["added"] == 0
        assert result["stats"]["removed"] == 0
        assert result["stats"]["similarity"] == 100.0

    def test_completely_different(self):
        service = TextService()
        result = service.diff_texts("aaa\nbbb\nccc", "xxx\nyyy\nzzz")
        assert result["identical"] is False
        assert result["stats"]["added"] == 3
        assert result["stats"]["removed"] == 3
        assert result["stats"]["unchanged"] == 0

    def test_single_line_added(self):
        service = TextService()
        result = service.diff_texts("line1\nline2", "line1\nline2\nline3")
        assert result["identical"] is False
        assert result["stats"]["added"] == 1
        assert result["stats"]["removed"] == 0
        assert result["stats"]["unchanged"] == 2

    def test_single_line_removed(self):
        service = TextService()
        result = service.diff_texts("line1\nline2\nline3", "line1\nline3")
        assert result["identical"] is False
        assert result["stats"]["removed"] == 1
        assert result["stats"]["unchanged"] == 2

    def test_line_modified(self):
        service = TextService()
        result = service.diff_texts("hello world", "hello python")
        assert result["identical"] is False
        assert result["stats"]["added"] == 1
        assert result["stats"]["removed"] == 1

    def test_empty_first_text(self):
        service = TextService()
        result = service.diff_texts("", "new content\nhere")
        assert result["identical"] is False
        assert result["stats"]["added"] == 2
        assert result["stats"]["removed"] == 0

    def test_empty_second_text(self):
        service = TextService()
        result = service.diff_texts("old content\nhere", "")
        assert result["identical"] is False
        assert result["stats"]["removed"] == 2
        assert result["stats"]["added"] == 0

    def test_both_empty(self):
        service = TextService()
        result = service.diff_texts("", "")
        assert result["identical"] is True
        assert result["stats"]["similarity"] == 100.0

    def test_multiline_diff(self):
        service = TextService()
        text1 = "line1\nline2\nline3\nline4\nline5"
        text2 = "line1\nmodified\nline3\nline4\nnew_line5\nextra"
        result = service.diff_texts(text1, text2)
        assert result["identical"] is False
        assert result["stats"]["unchanged"] == 3  # line1, line3, line4
        assert result["stats"]["removed"] == 2  # line2, line5
        assert result["stats"]["added"] == 3  # modified, new_line5, extra

    def test_similarity_percentage(self):
        service = TextService()
        # Mostly similar texts
        text1 = "the quick brown fox\njumps over\nthe lazy dog"
        text2 = "the quick brown cat\njumps over\nthe lazy dog"
        result = service.diff_texts(text1, text2)
        assert result["stats"]["similarity"] > 80.0

    def test_changes_structure(self):
        service = TextService()
        result = service.diff_texts("a\nb", "a\nc")
        changes = result["changes"]
        assert any(c["type"] == "equal" and c["content"] == "a" for c in changes)
        assert any(c["type"] == "removed" and c["content"] == "b" for c in changes)
        assert any(c["type"] == "added" and c["content"] == "c" for c in changes)

    def test_unified_diff_output(self):
        service = TextService()
        result = service.diff_texts("hello", "world")
        assert "---" in result["unified_diff"]
        assert "+++" in result["unified_diff"]

    def test_context_lines_parameter(self):
        service = TextService()
        text1 = "\n".join(f"line{i}" for i in range(20))
        text2 = text1.replace("line10", "CHANGED")
        result_small = service.diff_texts(text1, text2, context_lines=1)
        result_large = service.diff_texts(text1, text2, context_lines=5)
        # More context = longer unified diff
        assert len(result_large["unified_diff"]) >= len(result_small["unified_diff"])

    def test_whitespace_differences(self):
        service = TextService()
        result = service.diff_texts("hello world", "hello  world")
        assert result["identical"] is False

    def test_trailing_newline_difference(self):
        service = TextService()
        # "hello\n" vs "hello" — raw strings differ, but lines are the same
        # identical compares raw text, so these are NOT identical
        result = service.diff_texts("hello\n", "hello")
        # The splitlines produces same result, but raw text comparison differs
        assert result["stats"]["unchanged"] == 1

    def test_large_text(self):
        """Test with larger texts (edge case for performance)."""
        service = TextService()
        text1 = "\n".join(f"line {i}: some content here" for i in range(500))
        text2 = text1.replace("line 250: some content here", "line 250: MODIFIED")
        result = service.diff_texts(text1, text2)
        assert result["stats"]["unchanged"] == 499
        assert result["stats"]["added"] == 1
        assert result["stats"]["removed"] == 1


class TestDiffEndpoint:
    """Tests for the /api/v1/text/diff endpoint."""

    def test_basic_diff(self, test_client):
        resp = test_client.post(
            "/api/v1/text/diff",
            data={"text1": "hello\nworld", "text2": "hello\npython"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "changes" in data
        assert "stats" in data
        assert "unified_diff" in data
        assert data["identical"] is False

    def test_identical_texts_endpoint(self, test_client):
        resp = test_client.post(
            "/api/v1/text/diff",
            data={"text1": "same text", "text2": "same text"},
        )
        assert resp.status_code == 200
        assert resp.json()["identical"] is True

    def test_empty_texts(self, test_client):
        resp = test_client.post(
            "/api/v1/text/diff",
            data={"text1": "", "text2": ""},
        )
        assert resp.status_code == 200
        assert resp.json()["identical"] is True

    def test_text_too_large(self, test_client):
        large_text = "x" * 100_001
        resp = test_client.post(
            "/api/v1/text/diff",
            data={"text1": large_text, "text2": "small"},
        )
        assert resp.status_code == 422
        assert "too large" in resp.json()["detail"].lower()

    def test_custom_context_lines(self, test_client):
        resp = test_client.post(
            "/api/v1/text/diff",
            data={"text1": "a\nb\nc", "text2": "a\nx\nc", "context_lines": "1"},
        )
        assert resp.status_code == 200

    def test_context_lines_clamped(self, test_client):
        """Context lines should be clamped between 0 and 10."""
        resp = test_client.post(
            "/api/v1/text/diff",
            data={"text1": "a", "text2": "b", "context_lines": "99"},
        )
        assert resp.status_code == 200
