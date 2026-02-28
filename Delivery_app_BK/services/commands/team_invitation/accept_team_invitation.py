from Delivery_app_BK.errors import NotFound, PermissionDenied, ValidationFailed
from Delivery_app_BK.models import db, TeamInvites, User
from Delivery_app_BK.services.commands.auth.token_utils import build_user_tokens
from ...context import ServiceContext


def accept_team_invitation(ctx: ServiceContext, invitation_id: int):
    if invitation_id is None:
        raise ValidationFailed("Invitation id is required to accept an invitation.")
    if not ctx.user_id:
        raise ValidationFailed("User id is required to accept an invitation.")

    invite = db.session.get(TeamInvites, invitation_id)
    
    if not invite:
        raise NotFound(f"Team invitation with id '{invitation_id}' was not found.")

    if invite.target_user_id != ctx.user_id:
        raise PermissionDenied(
            "You are not authorized to accept this team invitation."
        )

    user = db.session.get(User, ctx.user_id)
    if not user:
        raise NotFound("User was not found for invitation acceptance.")

    if not user.old_team_id and not user.old_role_id:
        user.old_team_id = user.team_id
        user.old_role_id = user.user_role_id
        
    user.team_id = invite.team_id
    user.user_role_id = invite.user_role_id

    db.session.delete(invite)
    db.session.commit()
    db.session.refresh(user)

    return build_user_tokens(user, time_zone=ctx.identity.get("time_zone"))
