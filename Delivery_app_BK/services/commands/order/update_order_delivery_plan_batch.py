from __future__ import annotations

from sqlalchemy.exc import InvalidRequestError

from Delivery_app_BK.services.commands.order.update_order_delivery_plan import (
    update_orders_delivery_plan,
)
from Delivery_app_BK.services.context import ServiceContext
from Delivery_app_BK.services.domain.order.order_batch_selection import (
    resolve_order_batch_selection,
)
from Delivery_app_BK.services.requests.order.update_orders_delivery_plan_batch import (
    parse_update_orders_delivery_plan_batch_payload,
)
from Delivery_app_BK.models import db


def resolve_orders_selection(ctx: ServiceContext) -> dict:
    selection = parse_update_orders_delivery_plan_batch_payload(ctx.incoming_data)

    resolved = _run_selection_resolution_transaction(
        lambda: resolve_order_batch_selection(
            ctx=ctx,
            selection=selection,
            endpoint="resolve",
            include_order_ids=False,
        )
    )

    payload = {
        "signature": resolved.signature,
        "resolved_count": resolved.resolved_count,
    }
    if resolved.sample_ids:
        payload["sample_ids"] = resolved.sample_ids
    return payload


def update_orders_delivery_plan_batch(
    ctx: ServiceContext,
    plan_id: int,
) -> dict:
    selection = parse_update_orders_delivery_plan_batch_payload(ctx.incoming_data)
    print('Debugging: ', 'selection')
    print(selection)
    print('-------------')
    resolved = _run_selection_resolution_transaction(
        lambda: resolve_order_batch_selection(
            ctx=ctx,
            selection=selection,
            endpoint="batch_move",
            include_order_ids=True,
        )
    )

    updated_bundles = []
    if resolved.order_ids:
        updated_payload = update_orders_delivery_plan(ctx, resolved.order_ids, plan_id)
        updated_bundles = updated_payload.get("updated") or []

    return {
        "signature": resolved.signature,
        "resolved_count": resolved.resolved_count,
        "updated_count": len(updated_bundles),
        "updated_bundles": updated_bundles,
    }


def _run_selection_resolution_transaction(resolver):
    try:
        with db.session.begin():
            return resolver()
    except InvalidRequestError as exc:
        if "already begun" not in str(exc).lower():
            raise
        return resolver()
