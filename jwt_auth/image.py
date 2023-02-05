import json

import falcon
from authlib.jose import errors

from .config import load_config
from .jwt import validate_jwt
from .s3 import get_random_image


class RestrictedImageResource:
    def on_get(self, request: falcon.request.Request, response: falcon.response.Response):
        cfg = load_config()

        auth_header = request.headers.get("AUTHORIZATION")
        if auth_header is None:
            response.status = falcon.HTTP_UNAUTHORIZED
            response.text = json.dumps({"message": "Missing Authorization HTTP header"})
            return

        json_web_token = self.extract_json_web_token(auth_header)

        if json_web_token is None:
            response.status = falcon.HTTP_UNAUTHORIZED
            response.text = json.dumps({"message": "Invalid Authorization HTTP header"})
            return

        try:
            validate_jwt(cfg, json_web_token, roles=["CAN_VIEW_IMAGE"])
        except (errors.BadSignatureError, errors.ExpiredTokenError, errors.InvalidClaimError) as err:
            response.status = falcon.HTTP_FORBIDDEN
            response.text = json.dumps({"message": f"{err.error}; {err.description}"})
            return

        output = {"image": get_random_image(cfg)}
        response.text = json.dumps(output, ensure_ascii=False)

    @staticmethod
    def extract_json_web_token(header: str) -> str | None:
        header = header.strip()
        if not header.startswith("Bearer"):
            return None
        return header.split("Bearer", 1)[1].strip()
