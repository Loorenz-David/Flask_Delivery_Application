from Delivery_app_BK.errors import ValidationFailed
from Delivery_app_BK.models import db, User

from ...context import ServiceContext
from ...queries.get_instance import get_instance


# missing to configure invalidating token when a user gets kicked out.

def kick_team_memember(ctx: ServiceContext, user_id: int):
    if not user_id:
        raise ValidationFailed("User id is required to remove a team member.")

    user: User = get_instance(ctx, User, user_id)
  
    if user.old_team_id is None or user.old_role_id is None:
        raise ValidationFailed("User has no previous team or role to return to.")

    team_members = (
        db.session.query(User)
        .filter(User.team_id == user.team_id)
        .count()
    )
    if team_members <= 1:
        raise ValidationFailed("You cannot remove the only team member.")

    user.team_id = user.old_team_id
    user.user_role_id = user.old_role_id
    user.old_team_id = None
    user.old_role_id = None

    db.session.commit()
    return user
