import falcon

from .image import RestrictedImageResource
from .jwt import JWTResource

app = application = falcon.App()
app.add_route("/image", RestrictedImageResource())
app.add_route("/jwt", JWTResource())
