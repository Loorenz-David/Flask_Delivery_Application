from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from Delivery_app_BK.routers.utils.role_decorator import role_required


from . import user_bp
from Delivery_app_BK.routers.utils.response import Response
from Delivery_app_BK.models.managers.object_filler import ObjectFiller
from Delivery_app_BK.models import User
from Delivery_app_BK.services import (
    service_update_user,
    service_update_team,
    service_update_user_role,
    service_update_user_warehouse,
)


@user_bp.route("/update_user", methods=["PUT"])
@jwt_required()
@role_required([1,2,3])
def update_user():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    # Guard: only admins can modify other users
    try:
        payload = response.incoming_data or {}
        target_id = None
        if isinstance(payload, list) and payload:
            target_id = payload[0].get("id")
        elif isinstance(payload, dict):
            target_id = payload.get("id")

        identity_user_id = identity.get("user_id")
        identity_role_id = identity.get("role_id")

        if target_id is not None and identity_user_id is not None and target_id != identity_user_id:
            if identity_role_id != 1:
                response.set_error("Only admins can update other users.", 403)
                return response.build()

        # If attempting to change role_id, ensure not demoting the sole team member
        fields = None
        if isinstance(payload, list) and payload:
            fields = payload[0].get("fields")
        elif isinstance(payload, dict):
            fields = payload.get("fields")

        if isinstance(fields, dict) and "role_id" in fields:
            team_id = identity.get("team_id")
            if team_id is not None:
                team_users_count = User.query.filter_by(team_id=team_id).count()

                if team_users_count <= 1:
                    print("Guard triggered: cannot change role when only team member.")
                    response.set_message("Cannot change role when you are the only member of the team.")
                    response.set_error("Cannot change role when you are the only member of the team.", 400)
                    print("Guard triggered: cannot change role when only team member.")
                    return response.build()
    except Exception:
        # If guard parsing fails, fall through and let ObjectFiller handle validation
        pass

    ObjectFiller.fill_object(
        fill_function=service_update_user,
        response=response,
        reference="User",
        add_to_session=False,
        action_type="update",
    )

    return response.build()


@user_bp.route("/update_team", methods=["PUT"])
@jwt_required()
@role_required([1])
def update_team():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    ObjectFiller.fill_object(
        fill_function=service_update_team,
        response=response,
        reference="Team",
        add_to_session=False,
        action_type="update",
    )

    return response.build()


@user_bp.route("/update_user_role", methods=["PUT"])
@jwt_required()
@role_required([1])
def update_user_role():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    ObjectFiller.fill_object(
        fill_function=service_update_user_role,
        response=response,
        reference="User Role",
        add_to_session=False,
        action_type="update",
    )

    return response.build()


@user_bp.route("/update_user_warehouse", methods=["PUT"])
@jwt_required()
@role_required([1])
def update_user_warehouse():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    ObjectFiller.fill_object(
        fill_function=service_update_user_warehouse,
        response=response,
        reference="User Warehouse",
        add_to_session=False,
        action_type="update",
    )

    return response.build()
