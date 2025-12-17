from functools import wraps
from typing import Iterable

from flask_jwt_extended import get_jwt, verify_jwt_in_request

from .response import Response


def role_required(allowed_roles: Iterable[int] | None = None):
    """
    Decorator to enforce role-based access using the role_id stored in JWT claims.
    Usage:
        @jwt_required()
        @role_required([1, 2])
        def my_route(): ...
    """

    allowed_set = set(allowed_roles or [])

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Ensure a valid JWT is present even if @jwt_required is omitted.
            verify_jwt_in_request(optional=False)
            claims = get_jwt()
            response = Response(identity=claims)

            role_id = claims.get("role_id")
            if role_id is None:
                response.set_error("Role not found in token.", 410)
                return response.build()

            if allowed_set and role_id not in allowed_set:
                response.set_error("Insufficient role permissions.", 411)
                return response.build()

            return fn(*args, **kwargs)

        return wrapper

    return decorator
