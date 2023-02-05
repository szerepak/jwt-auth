import base64
import json
from datetime import datetime, timedelta

import falcon
from authlib.jose import JWTClaims, jwt

from .config import load_config


class JWTResource:
    def on_post(self, request: falcon.request.Request, response: falcon.response.Response):
        cfg: dict[str, str | None] = load_config()

        if not self.check_basic_authorization(cfg, request.headers):
            response.status = falcon.HTTP_UNAUTHORIZED
            return

        json_web_token: str = create_encoded_jwt(cfg, ["CAN_VIEW_IMAGE"])

        response.text = json.dumps({"jwt": json_web_token})

    @staticmethod
    def check_basic_authorization(config: dict[str, str | None], headers) -> bool:
        user_password: str = base64.b64encode(f"{config['USERNAME']}:{config['PASSWORD']}".encode()).decode()
        return headers.get("AUTHORIZATION") == user_password


def create_encoded_jwt(config: dict[str, str | None], roles: list[str]) -> str:
    return jwt.encode(
        header={"alg": "HS256", "typ": "JWT"},
        payload={
            "iss": "jwt-auth",
            "exp": int((datetime.utcnow() + timedelta(days=1)).timestamp()),
            "sub": config["USERNAME"],
            "roles": roles,
        },
        key=config["JWT_KEY"],
    ).decode()


def validate_jwt(config: dict[str, str | None], json_web_token: str, roles: list[str] | None = None) -> None:
    jwt_claims: JWTClaims = jwt.decode(
        json_web_token,
        key=config["JWT_KEY"],
        claims_options={
            "iss": {
                "essential": True,
                "value": "jwt-auth",
            },
            "sub": {
                "essential": True,
                "value": config["USERNAME"],
            },
            "exp": {
                "essential": True,
            },
            "roles": {"validate": lambda jwt_claims_obj, value: set(value) <= set(roles) if roles else True},
        },
    )
    jwt_claims.validate()
