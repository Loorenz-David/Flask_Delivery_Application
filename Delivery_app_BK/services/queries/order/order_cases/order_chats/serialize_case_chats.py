from typing import Type, List
from Delivery_app_BK.models import CaseChat

from Delivery_app_BK.services.context import ServiceContext
from Delivery_app_BK.services.queries.utils import map_return_values


def _unpack_case_chat(instance: CaseChat):
    creation_date = instance.creation_date
    return {
        "id": instance.id,
        "client_id": instance.client_id,
        "message": instance.message,
        "creation_date": creation_date.isoformat() if creation_date else None,
        "user_id": instance.user_id,
        "order_case_id": instance.order_case_id,
        "notification_reads": [
            {
                "reader_name": read.reader_name,
                "user_id": read.user_id,
                "seen_at": read.seen_at.isoformat() if read.seen_at else None,
            }
            for read in (instance.notification_reads or [])
        ],
    }


def unpack_case_chats(instances: List[CaseChat]):
    return [_unpack_case_chat(instance) for instance in instances]


def serialize_case_chats(instances: List[CaseChat], ctx: ServiceContext):
    unpacked_instances = unpack_case_chats(instances)
    return map_return_values(unpacked_instances, ctx, "case_chat")
