from functools import wraps
from typing import Iterable

from flask_jwt_extended import get_jwt, verify_jwt_in_request

from Delivery_app_BK.errors import PermissionDenied, ValidationFailed
from Delivery_app_BK.routers.http.response import Response

ADMIN = 1
ASSISTANT = 2
DRIVER = 3

def role_required(allowed_roles: Iterable[int] | None = None):
    """
    Decorator to enforce role-based access using the base_role_id stored in JWT claims.
    Usage:
        @jwt_required()
        @role_required([ADMIN, ASSISTANT])
        def my_route(): ...
    """

    allowed_set = set(allowed_roles or [])

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Ensure a valid JWT is present even if @jwt_required is omitted.
            verify_jwt_in_request(optional=False)
            claims = get_jwt()
            response = Response()

            base_role_id = claims.get("base_role_id")
            if base_role_id is None:
                return response.build_unsuccessful_response(
                    ValidationFailed("Role not found in token.")
                )

            if allowed_set and base_role_id not in allowed_set:
                return response.build_unsuccessful_response(
                    PermissionDenied("Insufficient role permissions.")
                )

            return fn(*args, **kwargs)

        return wrapper

    return decorator
