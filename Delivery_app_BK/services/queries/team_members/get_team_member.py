from Delivery_app_BK.models import User
from Delivery_app_BK.errors import NotFound

from ...context import ServiceContext
from ..get_instance import get_instance
from .serialize_team_members import serialize_team_members


def get_team_member(user_id: int, ctx: ServiceContext):
    found_user = get_instance(
        ctx=ctx,
        model=User,
        value=user_id,
    )

    if not found_user:
        raise NotFound(f"User with id: {user_id} does not exist.")

    serialized = serialize_team_members(
        instances=[found_user],
        ctx=ctx,
    )

    return {
        "team_member": serialized[0] if isinstance(serialized, list) else serialized
    }
