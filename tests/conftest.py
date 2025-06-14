import pytest
from unittest.mock import patch, MagicMock

@pytest.fixture(scope="module")
def client():
    with patch("docker.from_env") as mock_docker:
        # Mocked Docker Service
        mock_service = MagicMock()
        mock_service.name = "nginx_alpine"
        mock_service.attrs = {
            "UpdateStatus": {"State": "running"},
            "Endpoint": {
                "Ports": [{"PublishedPort": 8085, "TargetPort": 80}]
            },
            "Spec": {"Secrets": []}
        }
        mock_service.update.return_value = None  # for patch_config

        # Mock Docker Client
        mock_services = MagicMock()
        mock_services.create.return_value = mock_service
        mock_services.get.return_value = mock_service

        mock_docker.return_value.services = mock_services
        mock_docker.return_value.api.logs.return_value.decode.return_value = "log line 1\nlog line 2"

        from app.main import app
        from fastapi.testclient import TestClient
        return TestClient(app)
