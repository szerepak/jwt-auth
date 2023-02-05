import base64
from datetime import datetime, timedelta

import falcon
import pytest
from authlib.jose import errors, jwt
from freezegun import freeze_time

from jwt_auth.jwt import create_encoded_jwt, validate_jwt


def test_jwt__no_authorization_header(client):
    response = client.simulate_post("/jwt")
    assert response.status == falcon.HTTP_UNAUTHORIZED


def test_jwt__wrong_authorization_header(client):
    response = client.simulate_post(
        "/jwt", headers={"Authorization": base64.b64encode("wrong-username:wrong-password".encode()).decode()}
    )
    assert response.status == falcon.HTTP_UNAUTHORIZED


def test_jwt__ok(client, basic_auth_value):
    response = client.simulate_post("/jwt", headers={"Authorization": basic_auth_value})
    assert response.status == falcon.HTTP_OK
    assert response.json["jwt"]


def test_create_encoded_jwt(test_config):
    assert isinstance(create_encoded_jwt(test_config, ["CAN_VIEW_IMAGE"]), str)


def test_validate_jwt__ok(test_config, valid_jwt):
    assert validate_jwt(test_config, valid_jwt, ["CAN_VIEW_IMAGE"]) is None
    assert validate_jwt(test_config, valid_jwt) is None


def test_validate_jwt__invalid_jwt_key(test_config):
    json_web_token = jwt.encode(
        header={"alg": "HS256", "typ": "JWT"},
        payload={
            "iss": "invalid-test-issuer",
            "exp": int((datetime.utcnow() + timedelta(days=1)).timestamp()),
            "sub": test_config["USERNAME"],
        },
        key="invalid-test-jwt-key",
    ).decode()
    with pytest.raises(errors.BadSignatureError):
        validate_jwt(test_config, json_web_token)


def test_validate_jwt__expired_token(test_config):
    with freeze_time("2023-02-01"):
        json_web_token = create_encoded_jwt(test_config, ["CAN_VIEW_IMAGE"])

    with freeze_time("2023-02-03"):
        with pytest.raises(errors.ExpiredTokenError):
            validate_jwt(test_config, json_web_token)


def test_validate_jwt__invalid_subject(test_config):
    malformed_config = test_config.copy()
    malformed_config["USERNAME"] = "invalid-test-subject"
    json_web_token = create_encoded_jwt(malformed_config, ["CAN_VIEW_IMAGE"])
    with pytest.raises(errors.InvalidClaimError) as err:
        validate_jwt(test_config, json_web_token)
    assert err.value.description == 'Invalid claim "sub"'


def test_validate_jwt__invalid_roles(test_config, valid_jwt):
    with pytest.raises(errors.InvalidClaimError) as err:
        validate_jwt(test_config, valid_jwt, ["CAN_VIEW_TEXT"])
    assert err.value.description == 'Invalid claim "roles"'


def test_validate_jwt__invalid_issuer(test_config):
    json_web_token = jwt.encode(
        header={"alg": "HS256", "typ": "JWT"},
        payload={
            "iss": "invalid-test-issuer",
            "exp": int((datetime.utcnow() + timedelta(days=1)).timestamp()),
            "sub": test_config["USERNAME"],
        },
        key=test_config["JWT_KEY"],
    ).decode()

    with pytest.raises(errors.InvalidClaimError) as err:
        validate_jwt(test_config, json_web_token)
    assert err.value.description == 'Invalid claim "iss"'
