from Delivery_app_BK.errors import ValidationFailed
from Delivery_app_BK.models import db, DeliveryPlan, Team, Order, DeliveryPlanState
from ...context import ServiceContext
from ..base.update_instance import update_instance
from ..utils import extract_targets
from ...queries.get_instance import get_instance





def _split_plan_type_fields(fields: dict, plan_types: set[str]):
    has_plan_type = "plan_type" in fields
    plan_type_key = fields.get("plan_type")
    plan_type_fields = None

    if has_plan_type:
        if not plan_type_key:
            raise ValidationFailed("plan_type is required to update plan type fields.")
        if plan_type_key not in plan_types:
            raise ValidationFailed(f"Invalid plan_type: {plan_type_key}")

        plan_type_fields = fields.get(plan_type_key)
        if not plan_type_fields:
            raise ValidationFailed(
                f"Missing fields for plan type {plan_type_key}."
            )
        if not isinstance(plan_type_fields, dict):
            raise ValidationFailed(
                f"Plan type fields for {plan_type_key} must be a dictionary."
            )

        extra_plan_type_keys = [
            key
            for key in plan_types
            if key in fields and key != plan_type_key
        ]
        if extra_plan_type_keys:
            raise ValidationFailed(
                f"Unexpected plan type fields: {extra_plan_type_keys}."
            )
    else:
        plan_type_fields_keys = [
            key for key in plan_types if key in fields
        ]
        if plan_type_fields_keys:
            raise ValidationFailed("Missing plan_type for plan type fields.")

    plan_fields = dict(fields)
    if plan_type_key:
        plan_fields.pop("plan_type", None)
        plan_fields.pop(plan_type_key, None)

    return plan_fields, plan_type_key, plan_type_fields


def _update_plan_type_instance(
    ctx: ServiceContext,
    target_id: int | str,
    plan_type_key: str | None,
    plan_type_fields: dict | None,
):
    if not plan_type_key:
        return

    plan_instance = get_instance(ctx, DeliveryPlan, target_id)
    if plan_instance.plan_type != plan_type_key:
        raise ValidationFailed(
            f"Plan type cannot be changed from '{plan_instance.plan_type}' "
            f"to '{plan_type_key}'."
        )

    plan_type_instance = getattr(plan_instance, plan_type_key, None)
    if not plan_type_instance:
        raise ValidationFailed(
            f"Plan type instance '{plan_type_key}' was not found."
        )

    update_instance(
        ctx,
        plan_type_instance.__class__,
        plan_type_fields,
        plan_type_instance.id,
    )


def update_plan(ctx: ServiceContext):
    relationship_map = {
        "team_id": Team,
        "plan_state_id": DeliveryPlanState
    }
    ctx.set_relationship_map(relationship_map)
    instances = []

    for target in extract_targets(ctx):
        fields = target["fields"] or {}
        plan_fields, plan_type_key, plan_type_fields = _split_plan_type_fields(
            fields,
            DeliveryPlan.PLAN_TYPES,
        )


        _update_plan_type_instance(
            ctx,
            target["target_id"],
            plan_type_key,
            plan_type_fields,
        )

        instance = update_instance(ctx, DeliveryPlan, plan_fields, target["target_id"])
        instances.append(instance.id)
    db.session.commit()
    return instances
