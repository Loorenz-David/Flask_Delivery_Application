from datetime import timedelta
from flask_jwt_extended import create_access_token

# Local application imports 
from Delivery_app_BK.models import db, User,UserRole, BaseRole
from Delivery_app_BK.errors import ValidationFailed

from ...context import ServiceContext



def login_user_service( ctx:ServiceContext ):

    target_user = ctx.incoming_data

    if not target_user:
        raise ValidationFailed("Missing username and password.")

    if not target_user.get( "password" ):
        raise ValidationFailed( "Missing password." ) 

    if not target_user.get( "email" ):
        raise ValidationFailed( "Missing email." ) 
    
    user_query = db.session.query( User )
    user:User = user_query.filter( User.email == target_user.get( "email" )).first()

    if not user:
        raise ValidationFailed( "Incorrect login information." ) 
    
    if not user.check_password( target_user.get( "password" ) ):
        raise ValidationFailed( "Incorrect login information." ) 
    

    user_role: UserRole = user.user_role
    base_role:BaseRole = user_role.base_role
    
    identity_data = str(user.id)
    claims = {"user_id": user.id, "team_id": user.team_id, "user_role_id": user_role.id, "base_role_id": base_role.id }

    access_token  = create_access_token(identity=identity_data, additional_claims=claims)
    refresh_token = create_access_token(identity=identity_data, additional_claims=claims)
    socket_token = create_access_token(
                identity=identity_data, additional_claims=claims, expires_delta=timedelta(hours=24)
            )
    
    user_object = {
        "username": user.username,
        "profile_picture": user.profile_picture,
        "user_role_id": user.user_role_id,
        "base_role_id": base_role.id,
        "show_app_tutorial": user.show_app_tutorial,
    }
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "socket_token": socket_token,
        "user": user_object,
    }