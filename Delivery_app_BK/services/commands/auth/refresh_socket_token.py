from datetime import timedelta
from flask_jwt_extended import create_access_token

# Local application imports 

from ...context import ServiceContext



def refresh_socket_token( ctx:ServiceContext ):

    identity = ctx.identity

    identity_data = str( identity.get( "user_id" ) )
    claims = {
        "user_id": identity.get("user_id"),
        "team_id": identity.get("team_id"),
        "user_role_id": identity.get("user_role_id"),
        "base_role_id": identity.get("base_role_id"),
        "time_zone": identity.get("time_zone") or "UTC",
    }

    socket_token = create_access_token(
        identity=identity_data, additional_claims=claims, expires_delta=timedelta(hours=24)
    )
    
    return {
        "socket_token": socket_token
    }
