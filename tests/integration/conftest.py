# tests/integration/conftest.py

import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_wug_api(requests_mock):
    """Mock a WhatsUp Gold API com respostas padrão."""
    base_url = "https://mock-wug-server:9644/api/v1"

    # Mock token endpoint
    requests_mock.post(
        f"{base_url}/token",
        json={"access_token": "mock_token", "expires_in": 3600},
        status_code=200
    )

    # Mock devices endpoint
    requests_mock.get(
        f"{base_url}/device-groups/0/devices",
        json={
            "data": {
                "devices": [
                    {"name": "Device-1", "networkAddress": "1.1.1.1", "bestState": "Up"},
                    {"name": "Device-2", "networkAddress": "2.2.2.2", "bestState": "Down"},
                    {"name": "Device-3", "networkAddress": "3.3.3.3", "bestState": "Maintenance"},
                    {"name": "Device-4", "networkAddress": "4.4.4.4", "bestState": "Unknown"},
                ]
            }
        },
        status_code=200
    )

    # Mock reports endpoint
    requests_mock.get(
        f"{base_url}/devices/1/reports/cpu-utilization",
        json={"report": "data"},
        status_code=200
    )

    return requests_mock
