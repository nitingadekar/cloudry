"""Shared test fixtures and configuration."""

import os
from unittest.mock import patch

import pytest


@pytest.fixture(autouse=True)
def mock_env_vars():
    """Provide default environment variables for all tests."""
    env = {
        "ENVIRONMENT": "test",
        "CORS_ORIGINS": "http://localhost:3000",
        "TURNSTILE_SECRET_KEY": "test-secret-key",
        "TURNSTILE_ENABLED": "false",
        "RATE_LIMIT_PER_MINUTE": "100",
        "MAX_FILE_SIZE_MB": "20",
        "LOG_LEVEL": "warning",
    }
    with patch.dict(os.environ, env, clear=False):
        yield


@pytest.fixture
def test_client():
    """Create a FastAPI test client."""
    from fastapi.testclient import TestClient

    from src.app import app

    return TestClient(app)
