"""Tests for hash calculation service."""

from src.services.hash_service import HashService


def test_calculate_hashes():
    service = HashService()
    content = b"Hello, World!"
    hashes = service.calculate(content)

    assert "md5" in hashes
    assert "sha1" in hashes
    assert "sha256" in hashes
    # Known hash values for "Hello, World!"
    assert hashes["md5"] == "65a8e27d8879283831b664bd8b7f0ad4"
    assert hashes["sha256"] == "dffd6021bb2bd5b0af676290809ec3a53191dd81c7f70a4b28688a362182986f"


def test_calculate_hash_endpoint(test_client):
    resp = test_client.post(
        "/api/v1/hash/calculate",
        files={"file": ("test.txt", b"Hello, World!", "text/plain")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["filename"] == "test.txt"
    assert data["size_bytes"] == 13
    assert data["hashes"]["md5"] == "65a8e27d8879283831b664bd8b7f0ad4"


def test_empty_file_hash(test_client):
    resp = test_client.post(
        "/api/v1/hash/calculate",
        files={"file": ("empty.txt", b"", "text/plain")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["size_bytes"] == 0
    # MD5 of empty string
    assert data["hashes"]["md5"] == "d41d8cd98f00b204e9800998ecf8427e"
