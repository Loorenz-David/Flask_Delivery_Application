import random
from flask import request
from sqlalchemy.exc import IntegrityError

from Delivery_app_BK.models import db
from Delivery_app_BK.models.managers.object_validators import DataStructureValidators
from Delivery_app_BK.routers.utils.response import Response
from Delivery_app_BK.services import service_create_team, service_create_user

from . import user_bp
from .user_bootstrap_defaults import bootstrap_team_defaults


@user_bp.route("/register_user", methods=["POST"])
def register_user():
    incoming_data = request.get_json(silent=True)
    

    response = Response(incoming_data=incoming_data)
    
    if response.error:
        return response.build()

    try:
        payload = response.incoming_data or {}
        user_entries = DataStructureValidators.is_list_of_dicts(payload)
    except ValueError as err:
        response.set_error(message=str(err), status=400)
        response.set_message("Validation failed")
        return response.build()

    created_users = []

    try:
        for entry in user_entries:
            team_payload = {"name": f"Team {entry.get('name')} {random.randint(10000,99999)}"}  # Temporary team name generation
            if not isinstance(team_payload, dict):
                raise ValueError("Registration requires a team object with at least a name")

            user_fields = {key: value for key, value in entry.items() if key != "team"}
            username = user_fields.pop("name", None)
            if username and not user_fields.get("username"):
                user_fields["username"] = username

            team_result = service_create_team(team_payload)
            if team_result["status"] != "ok":
                raise ValueError("Unable to create team")
            team_instance = team_result["instance"]
            db.session.add(team_instance)
            db.session.flush()
            
            user_fields["team_id"] = team_instance.id
            user_fields["role_id"] = 1  # Default role assignment

            identity_override = {"team_id": team_instance.id, "role_id": 1}  # Assuming role_id 1 is for admin or default role
           
            user_result = service_create_user(user_fields, identity=identity_override, skip_team_check=True)
            if user_result["status"] != "ok":
                raise ValueError("Unable to create user")
            user_instance = user_result["instance"]
            db.session.add(user_instance)

            bootstrap_team_defaults(identity_override)
            
            created_users.append(
                {
                    "user_id": user_instance.id,
                    "email": getattr(user_instance, "email", None),
                    "team_id": team_instance.id,
                    "team_name": getattr(team_instance, "name", None),
                }
            )

        db.session.commit()
        response.set_message("User registered successfully")
        response.set_payload(created_users[0] if len(created_users) == 1 else created_users)
    except IntegrityError as err:
        db.session.rollback()
        readable = response.get_unique_error_message(err)
        response.set_error(message=readable or str(err.orig), status=400)
        response.set_message(readable or "Failed to register user due to duplicate data.")
    except Exception as err:
        print(err)
        db.session.rollback()
        response.set_error(message=str(err), status=400)
        response.set_message("Failed to register user")
    
    return response.build()
