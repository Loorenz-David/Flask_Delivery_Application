from Delivery_app_BK.models import InternationalShippingPlan
from ...context import ServiceContext
from ..utils import map_return_values


def serialize_international_shipping_plan(instance: InternationalShippingPlan, ctx: ServiceContext):
    unpacked_instances = [{
        "id": instance.id,
        "client_id": instance.client_id,
        "carrier_name": instance.carrier_name,
        "delivery_plan_id": instance.delivery_plan_id,
    }]
    mapped_instances = map_return_values(
        unpacked_instances, ctx, "international_shipping_plan"
    )
    return mapped_instances[0] if isinstance(mapped_instances, list) else mapped_instances
