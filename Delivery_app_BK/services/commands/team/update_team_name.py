

from Delivery_app_BK.errors import ValidationFailed
from Delivery_app_BK.models import Team, db
from Delivery_app_BK.services.context import ServiceContext
from Delivery_app_BK.services.queries.get_instance import get_instance


def update_team_name(ctx: ServiceContext):
    if not ctx.team_id:
        raise ValidationFailed("Team id is required to update team name.")

    incoming_data = ctx.incoming_data or {}
    name = incoming_data.get("name") or incoming_data.get("team_name")
    if not isinstance(name, str) or not name.strip():
        raise ValidationFailed("Team name is required to update team name.")
    name = name.strip()

    team: Team = get_instance(ctx=ctx, model=Team, value=ctx.team_id)
    team.name = name
    db.session.commit()
    return {"team": {"id": team.id, "name": team.name}}
