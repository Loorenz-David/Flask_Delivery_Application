from typing import Type
from flask_sqlalchemy.model import Model

from ....context import ServiceContext
from ...utils import map_return_values


def serialize_order_chats(instances: Type[Model], ctx: ServiceContext):
    unpacked_instances = []

    for instance in instances:
        creation_date = instance.creation_date
        unpacked = {
            "id": instance.id,
            "client_id": instance.client_id,
            "message": instance.message,
            "sender_name": instance.sender_name,
            "creation_date": creation_date.isoformat() if creation_date else None,
            "user_id": instance.user_id,
            "order_id": instance.order_id,
            "notification_reads": [
                {
                    "reader_name": read.reader_name,
                    "user_id": read.user_id,
                    "seen_at": read.seen_at.isoformat() if read.seen_at else None,
                }
                for read in (instance.notification_reads or [])
            ],
        }
        unpacked_instances.append(unpacked)

    return map_return_values(unpacked_instances, ctx, "order_chat")
