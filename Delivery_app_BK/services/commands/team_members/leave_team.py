from Delivery_app_BK.errors import ValidationFailed
from Delivery_app_BK.models import db, User

from ...context import ServiceContext
from ...queries.get_instance import get_instance
from Delivery_app_BK.services.commands.auth.token_utils import build_user_tokens


def leave_team(ctx: ServiceContext):
    if not ctx.user_id:
        raise ValidationFailed("User id is required to leave a team.")

    user: User = get_instance(ctx, User, ctx.user_id)

    if user.old_team_id is None or user.old_role_id is None:
        raise ValidationFailed("No previous team or role to return to.")

    team_members = (
        db.session.query(User)
        .filter(User.team_id == user.team_id)
        .count()
    )
    if team_members <= 1:
        raise ValidationFailed("You cannot leave a team with only one member.")

    user.team_id = user.old_team_id
    user.user_role_id = user.old_role_id
    user.old_team_id = None
    user.old_role_id = None

    db.session.commit()

    return build_user_tokens(user, time_zone=ctx.identity.get("time_zone"))
