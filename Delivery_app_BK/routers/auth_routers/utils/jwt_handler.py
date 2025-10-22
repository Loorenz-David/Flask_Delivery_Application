from flask_jwt_extended import JWTManager
from Delivery_app_BK.routers.utils.response import Response

jwt = JWTManager()

@jwt.unauthorized_loader
def missing_token_callback(error):
    response = Response()
    response.set_error(message="Missing Authorization Header", status=401)
    return response.build()

@jwt.invalid_token_loader
def invalid_token_callback(error):
    response = Response()
    response.set_error(message="Invalid token", status=422)
    return response.build()

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    response = Response()
    response.set_error(message="Token has expired", status=401)
    return response.build()