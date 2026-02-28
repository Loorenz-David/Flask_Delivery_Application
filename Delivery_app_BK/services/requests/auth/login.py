from dataclasses import dataclass

from Delivery_app_BK.errors import ValidationFailed
from Delivery_app_BK.services.requests.common.types import (
    parse_required_time_zone,
    validate_str,
)


@dataclass(frozen=True)
class LoginRequest:
    email: str
    password: str
    time_zone: str


def parse_login_request(raw: dict) -> LoginRequest:
    if not isinstance(raw, dict):
        raise ValidationFailed("Payload must be an object.")

    email = validate_str(raw.get("email"), field="email")
    password = validate_str(raw.get("password"), field="password")
    time_zone = parse_required_time_zone(raw.get("time_zone"), field="time_zone")

    return LoginRequest(
        email=email,
        password=password,
        time_zone=time_zone,
    )
