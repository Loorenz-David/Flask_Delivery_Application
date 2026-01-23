
from Delivery_app_BK.models import User

from ...context import ServiceContext
from ..utils import map_return_values


def serialize_user(instance: User, ctx: ServiceContext):

    
    last_online = instance.last_online
    unpacked_instances = [{
        "id": instance.id,
        "client_id": instance.client_id,
        "username": instance.username,
        "email": instance.email,
        "phone_number": instance.phone_number,
        "user_role_id": instance.user_role_id,
        "profile_picture": instance.profile_picture,
        "show_app_tutorial": instance.show_app_tutorial,
    }]
    mapped_instances = map_return_values(unpacked_instances, ctx, "user")
    return mapped_instances[0] if isinstance(mapped_instances, list) else mapped_instances
