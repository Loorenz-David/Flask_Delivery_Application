from flask import request
from flask_jwt_extended import jwt_required, get_jwt, create_access_token, create_refresh_token
from Delivery_app_BK.routers.utils.role_decorator import role_required

from . import user_bp
from Delivery_app_BK.models import db, User, Team, TeamInvitesSend, UserTeamInvitationsReceived
from Delivery_app_BK.routers.utils.response import Response


""" all these routers are not using the object searcher and other object managers made
for handling this logic and simplyfying the code for now due to time constraints."""

def _require_team(identity: dict, response: Response) -> int | None:
    team_id = identity.get("team_id")
    if team_id is None:
        response.set_error("Team not found in identity.", 403)
    return team_id


def _require_user(identity: dict, response: Response) -> int | None:
    user_id = identity.get("user_id")
    if user_id is None:
        response.set_error("User not found in identity.", 403)
    return user_id


@user_bp.route("/send_team_invitation", methods=["POST"])
@jwt_required()
@role_required([1])
def send_team_invitation():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    team_id = _require_team(identity, response)
    if response.error:
        return response.build()

    payload = response.incoming_data or {}
    username = (payload.get("username") or "").strip()
    email = (payload.get("email") or "").strip()
    role_id = payload.get("role_id")

    if not username or not email:
        response.set_error("username and email are required to send an invite.", 400)
        return response.build()

    try:
        team = Team.query.filter_by(id=team_id).first()
        if not team:
            response.set_error("Team not found.", 404)
            return response.build()

        invited_user = User.query.filter_by(username=username, email=email).first()

        if invited_user:
            received_invite = UserTeamInvitationsReceived(
                user_id=invited_user.id,
                from_team_id=team_id,
                from_team_name=team.name,
                role_id=role_id,
            )
            db.session.add(received_invite)

        sent_invite = TeamInvitesSend(
            team_id=team_id,
            user_id=invited_user.id if invited_user else None,
            username=username,
            email=email,
            role_id=role_id,
        )
        db.session.add(sent_invite)
        db.session.commit()

        response.set_payload({"invite_id": sent_invite.id})
        response.set_message("Invitation sent.")
        return response.build()
    except Exception as e:
        db.session.rollback()
        response.set_error(f"Failed to send invitation: {str(e)}", 500)
        return response.build()


@user_bp.route("/get_received_invitations", methods=["GET"])
@jwt_required()
@role_required([1, 2, 3])
def get_received_invitations():
    identity = get_jwt()
    response = Response(identity=identity)
    user_id = _require_user(identity, response)
    if response.error:
        return response.build()
    try:
        invitations = (
            UserTeamInvitationsReceived.query.filter_by(user_id=user_id)
            .order_by(UserTeamInvitationsReceived.date.desc())
            .all()
        )
        items = [
            {
                "id": invite.id,
                "team_name": invite.from_team_name,
                "date": invite.date,
            }
            for invite in invitations
        ]
        response.set_payload({"items": items})
        return response.build()
    except Exception as e:
        response.set_error(f"Failed to fetch invitations: {str(e)}", 500)
        return response.build()


@user_bp.route("/get_sent_invitations", methods=["GET"])
@jwt_required()
@role_required([1])
def get_sent_invitations():
    identity = get_jwt()
    response = Response(identity=identity)
    team_id = _require_team(identity, response)
    if response.error:
        return response.build()
    try:
        invitations = (
            TeamInvitesSend.query.filter_by(team_id=team_id)
            .order_by(TeamInvitesSend.date.desc())
            .all()
        )
        items = [
            {
                "id": invite.id,
                "username": invite.username,
                "email": invite.email,
                "date": invite.date,
            }
            for invite in invitations
        ]
        response.set_payload({"items": items})
        return response.build()
    except Exception as e:
        response.set_error(f"Failed to fetch sent invitations: {str(e)}", 500)
        return response.build()


@user_bp.route("/delete_invites_sent", methods=["DELETE"])
@jwt_required()
@role_required([1])
def delete_invites_sent():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)
    team_id = _require_team(identity, response)
    if response.error:
        return response.build()

    payload = response.incoming_data or {}
    sent_invite_id = payload.get("sent_invite_id")
    if not isinstance(sent_invite_id, int):
        response.set_error("sent_invite_id is required.", 400)
        return response.build()

    try:
        invite = TeamInvitesSend.query.filter_by(id=sent_invite_id, team_id=team_id).first()
        if not invite:
            response.set_error("Invitation not found.", 404)
            return response.build()

        received_invites = UserTeamInvitationsReceived.query.filter_by(
            from_team_id=team_id,
        )
        if invite.user_id:
            received_invites = received_invites.filter_by(user_id=invite.user_id)
        received_invite = received_invites.first()

        db.session.delete(invite)
        if received_invite:
            db.session.delete(received_invite)
        db.session.commit()
        response.set_message("Invitation deleted.")
        return response.build()
    except Exception as e:
        db.session.rollback()
        response.set_error(f"Failed to delete invitation: {str(e)}", 500)
        return response.build()


@user_bp.route("/interactions_invites_received", methods=["POST"])
@jwt_required()
@role_required([1, 2, 3])
def interactions_invites_received():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)
    user_id = _require_user(identity, response)
    if response.error:
        return response.build()

    payload = response.incoming_data or {}
    invite_id = payload.get("invitation_instance_id")
    action = (payload.get("action") or "").lower()
    if not isinstance(invite_id, int) or action not in {"accept", "reject"}:
        response.set_error("invitation_instance_id and valid action are required.", 400)
        return response.build()

    try:
        invitation = UserTeamInvitationsReceived.query.filter_by(id=invite_id, user_id=user_id).first()
        if not invitation:
            response.set_error("Invitation not found.", 404)
            return response.build()

        if action == "reject":
            db.session.delete(invitation)
            db.session.commit()
            response.set_message("Invitation rejected.")
            return response.build()

        user = User.query.filter_by(id=user_id).first()
        if not user:
            response.set_error("User not found.", 404)
            return response.build()

        target_team = Team.query.filter_by(id=invitation.from_team_id).first()
        if not target_team:
            response.set_error("team does not exist any more", 400)
            return response.build()

        user.old_team_id = user.team_id
        user.old_role_id = user.role_id
        user.team_id = invitation.from_team_id
        if invitation.role_id is not None:
            user.role_id = invitation.role_id

        sent_invite = (
            TeamInvitesSend.query.filter_by(team_id=invitation.from_team_id, user_id=user_id).first()
            or TeamInvitesSend.query.filter_by(team_id=invitation.from_team_id, email=user.email).first()
            or TeamInvitesSend.query.filter_by(team_id=invitation.from_team_id, username=user.username).first()
        )

        db.session.delete(invitation)
        if sent_invite:
            db.session.delete(sent_invite)
        db.session.commit()

        identity_value = str(user.id)
        claims = {"user_id": user.id, "team_id": user.team_id, "role_id": user.role_id}
        access_token = create_access_token(identity=identity_value, additional_claims=claims)
        refresh_token = create_refresh_token(identity=identity_value, additional_claims=claims)

        response.set_payload(
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
            }
        )
        response.set_message("Invitation accepted.")
        return response.build()
    except Exception as e:
        db.session.rollback()
        response.set_error(f"Failed to process invitation: {str(e)}", 500)
        return response.build()


@user_bp.route("/leave_team", methods=["POST"])
@jwt_required()
@role_required([1, 2, 3])
def leave_team():
    identity = get_jwt()
    response = Response(identity=identity)
    user_id = _require_user(identity, response)
    team_id = _require_team(identity, response)
    if response.error:
        return response.build()

    try:
        user = User.query.filter_by(id=user_id, team_id=team_id).first()
        if not user:
            response.set_error("User not found.", 404)
            return response.build()

        if user.old_team_id is None:
            response.set_error("No previous team to return to.", 400)
            return response.build()

        user.team_id = user.old_team_id
        user.old_team_id = None

        if user.old_role_id is not None:
            user.role_id = user.old_role_id
            user.old_role_id = None

        db.session.commit()
        identity_value = str(user.id)
        claims = {"user_id": user.id, "team_id": user.team_id, "role_id": user.role_id}
        access_token = create_access_token(identity=identity_value, additional_claims=claims)
        refresh_token = create_refresh_token(identity=identity_value, additional_claims=claims)
        response.set_payload(
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
            }
        )
        response.set_message("Left team successfully.")
        return response.build()
    except Exception as e:
        db.session.rollback()
        response.set_error(f"Failed to leave team: {str(e)}", 500)
        return response.build()


@user_bp.route("/kick_user_from_team", methods=["POST"])
@jwt_required()
@role_required([1])
def kick_user_from_team():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)
    team_id = _require_team(identity, response)
    if response.error:
        return response.build()

    payload = response.incoming_data or {}
    username = (payload.get("username") or "").strip()
    email = (payload.get("email") or "").strip()
    if not username or not email:
        response.set_error("username and email are required.", 400)
        return response.build()

    try:
        user = User.query.filter_by(username=username, email=email, team_id=team_id).first()
        if not user:
            response.set_error("User not found in this team.", 404)
            return response.build()

        if user.old_team_id is None:
            response.set_error("User has no previous team to return to.", 400)
            return response.build()

        user.team_id = user.old_team_id
        user.old_team_id = None

        if user.old_role_id is not None:
            user.role_id = user.old_role_id
            user.old_role_id = None

        db.session.commit()
        response.set_message("User removed from team.")
        return response.build()
    except Exception as e:
        db.session.rollback()
        response.set_error(f"Failed to remove user from team: {str(e)}", 500)
        return response.build()
