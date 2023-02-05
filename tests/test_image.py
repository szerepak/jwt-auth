from unittest.mock import patch

import falcon
from authlib.jose import errors


def test_image_endpoint__no_authorization_header(client):
    response = client.simulate_get("/image")
    assert response.status == falcon.HTTP_UNAUTHORIZED
    assert response.json == {"message": "Missing Authorization HTTP header"}


def test_image_endpoint__wrong_authorization_header(client, basic_auth_value):
    response = client.simulate_get("/image", headers={"Authorization": basic_auth_value})
    assert response.status == falcon.HTTP_UNAUTHORIZED
    assert response.json == {"message": "Invalid Authorization HTTP header"}


def test_image_endpoint__bad_signature(client, valid_jwt):
    with patch("jwt_auth.image.validate_jwt", side_effect=errors.BadSignatureError(result="")):
        response = client.simulate_get("/image", headers={"Authorization": f"Bearer {valid_jwt}"})
    assert response.status == falcon.HTTP_FORBIDDEN
    assert response.json == {"message": "bad_signature; "}


def test_image_endpoint__expired_token(client, valid_jwt):
    with patch("jwt_auth.image.validate_jwt", side_effect=errors.ExpiredTokenError()):
        response = client.simulate_get("/image", headers={"Authorization": f"Bearer {valid_jwt}"})
    assert response.status == falcon.HTTP_FORBIDDEN
    assert response.json == {"message": "expired_token; The token is expired"}


def test_image_endpoint__invalid_roles(client, valid_jwt):
    with patch("jwt_auth.image.validate_jwt", side_effect=errors.InvalidClaimError(claim="roles")):
        response = client.simulate_get("/image", headers={"Authorization": f"Bearer {valid_jwt}"})
    assert response.status == falcon.HTTP_FORBIDDEN
    assert response.json == {"message": 'invalid_claim; Invalid claim "roles"'}


@patch("jwt_auth.image.get_random_image", return_value="https://test.s3.amazonaws.com/nezuko/test.jpg")
def test_image_endpoint__ok(mock, client, valid_jwt):
    response = client.simulate_get("/image", headers={"Authorization": f"Bearer {valid_jwt}"})
    assert response.status == falcon.HTTP_OK
    assert response.json == {"image": mock.return_value}
