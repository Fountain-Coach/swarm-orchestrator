import pytest
from unittest.mock import patch, MagicMock

@pytest.fixture(scope="module")
def client():
    with patch("docker.from_env") as mock_docker:
        mock_docker.return_value = MagicMock()
        # Import AFTER patching
        from app.main import app
        from fastapi.testclient import TestClient
        return TestClient(app)
