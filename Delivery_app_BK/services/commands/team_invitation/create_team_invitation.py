from Delivery_app_BK.errors import ValidationFailed, NotFound
from Delivery_app_BK.models import db, Team, TeamInvites, User
from ...context import ServiceContext
from ..base.create_instance import create_instance
from ..utils import extract_fields, build_create_result


def create_team_invitation(ctx: ServiceContext):
    if not ctx.team_id:
        raise ValidationFailed("Team id is required to create a team invitation.")

    team = db.session.get(Team, ctx.team_id)
    if not team:
        raise NotFound("Team was not found for invitation creation.")

    instances = []
    field_set = extract_fields(ctx, return_single = True )

    
    fields = dict(field_set)
    target_user = fields.pop("target_user", None)
    fields.pop("target_user_id", None)
    fields.pop("team_id", None)
    fields.pop("from_team_name", None)
    fields.pop("target_username", None)
    fields.pop("target_email", None)


    if not isinstance(target_user, dict):
        raise ValidationFailed(
            "Missing 'target_user' with 'email' and 'username'."
        )

    email = target_user.get("email")
    username = target_user.get("username")
    if not email or not username:
        raise ValidationFailed(
            "Target user must include both 'email' and 'username'."
        )

    user = (
        db.session.query(User)
        .filter(User.email == email, User.username == username)
        .first()
    )
    if not user:
        raise NotFound(
            f"User with username '{username}' and email '{email}' was not found."
        )
    
    if user.id == ctx.user_id:
        raise ValidationFailed( "Cannot sent invitation to your self.")

    fields["team_id"] = team.id
    fields["from_team_name"] = team.name
    fields["target_username"] = user.username
    fields["target_email"] = user.email

    instance: TeamInvites = create_instance(ctx, TeamInvites, fields)
    instance.target_user_id = user.id
    

    db.session.add(instances)
    db.session.flush()
    result = build_create_result(ctx, [instance] )
    db.session.commit()
    return {"team_invites":result}
