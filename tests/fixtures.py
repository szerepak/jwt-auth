# pylint: disable=redefined-outer-name
import base64
from unittest.mock import patch

import pytest
from falcon import testing

from jwt_auth.app import app
from jwt_auth.jwt import create_encoded_jwt


@pytest.fixture
def client() -> testing.TestClient:
    return testing.TestClient(app)


@pytest.fixture(scope="session")
def test_config() -> dict[str, str | None]:
    return {
        "USERNAME": "test-username",
        "PASSWORD": "test-password",
        "JWT_KEY": "test-secret-jwt",
    }


@pytest.fixture(autouse=True)
def config(test_config: dict[str, str | None]) -> None:
    with patch("jwt_auth.image.load_config", return_value=test_config):
        with patch("jwt_auth.jwt.load_config", return_value=test_config):
            yield


@pytest.fixture(scope="session")
def basic_auth_value() -> str:
    return base64.b64encode("test-username:test-password".encode()).decode()


@pytest.fixture(scope="session")
def valid_jwt(test_config: dict[str, str | None]) -> str:
    return create_encoded_jwt(test_config, ["CAN_VIEW_IMAGE"])
