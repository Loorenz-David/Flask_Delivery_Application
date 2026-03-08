from datetime import timedelta
from flask_jwt_extended import create_access_token, create_refresh_token

from Delivery_app_BK.models import User,Team, UserRole, BaseRole


def _build_auth_claims(user: User, *, time_zone: str | None) -> dict:
    user_role: UserRole = user.user_role
    base_role: BaseRole = user_role.base_role
    effective_time_zone = time_zone or "UTC"

    return {
        "user_id": user.id,
        "team_id": user.team_id,
        "user_role_id": user_role.id,
        "base_role_id": base_role.id,
        "time_zone": effective_time_zone,
    }


def build_user_tokens(user: User) -> dict:
    user_role: UserRole = user.user_role
    base_role: BaseRole = user_role.base_role
    team:Team = user.team
    identity_data = str(user.id)
    effective_time_zone = team.time_zone or "UTC"

    claims = _build_auth_claims(user, time_zone=effective_time_zone)

    access_token = create_access_token(identity=identity_data, additional_claims=claims)
    refresh_token = create_refresh_token(identity=identity_data, additional_claims=claims)
    socket_token = create_access_token(
        identity=identity_data, additional_claims=claims, expires_delta=timedelta(hours=24)
    )

    user_object = {
        "username": user.username,
        "profile_picture": user.profile_picture,
        "user_role_id": user.user_role_id,
        "base_role_id": base_role.id,
        "show_app_tutorial": user.show_app_tutorial,
        "id": user.id,
        "team_name":user.team.name,

    }

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "socket_token": socket_token,
        "user": user_object,
    }
