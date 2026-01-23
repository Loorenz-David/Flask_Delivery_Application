from typing import Type, TypeAlias
from Delivery_app_BK.errors import ValidationFailed
from Delivery_app_BK.models import db, DeliveryPlan, PlanState, Team, Order ,LocalDeliveryPlan, InternationalShippingPlan, StorePickupPlan
from ...context import ServiceContext
from ..base.create_instance import create_instance
from ..utils import extract_fields, build_create_result


plan_type_map = {
    "local_delivery": LocalDeliveryPlan,
    "international_shipping": InternationalShippingPlan,
    "store_pickup": StorePickupPlan
}

def create_plan(ctx: ServiceContext):
    relationship_map = {
        "team_id": Team,
        "orders": Order,
        "plan_state": PlanState,
        "state_id": PlanState
    }
    ctx.set_relationship_map(relationship_map)
    plan_instances = []
    plan_type_instances = []

    for field_set in extract_fields(ctx):
       
        plan_type = field_set.get( "plan_type", None )
        fields_plan_type = field_set.pop( plan_type, None )
        
        if not plan_type :
            raise ValidationFailed( "Missing plan_type. ")
        if not fields_plan_type:
            raise ValidationFailed( f"Missing fields for plan type { plan_type }. ")
        if plan_type not in plan_type_map:
            raise ValidationFailed(f"Invalid plan_type: {plan_type}")
        
        PlanTypeModel = plan_type_map.get( plan_type )

        plan_instance = create_instance( ctx, DeliveryPlan, field_set)
        plan_type_instance = create_instance( ctx, PlanTypeModel, fields_plan_type)

        setattr( plan_instance, plan_type, plan_type_instance )

        plan_instances.append( plan_instance )
        plan_type_instances.append( plan_type_instance )

    db.session.add_all(plan_instances)
    db.session.add_all(plan_type_instances)
    db.session.flush()
    plan_results = build_create_result(ctx, plan_instances)
    plan_type_results = build_create_result(ctx, plan_type_instances)
    db.session.commit()

    result = {"delivery_plan": plan_results, "plan_type": plan_type_results }
    return result
