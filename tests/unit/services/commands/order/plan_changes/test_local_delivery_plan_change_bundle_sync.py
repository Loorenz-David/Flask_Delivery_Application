from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

from Delivery_app_BK.services.commands.order.plan_changes import local_delivery as module
from Delivery_app_BK.services.commands.order.plan_changes.types import PlanChangeApplyContext
from Delivery_app_BK.services.commands.plan.local_delivery.route_solution.plan_sync import (
    incremental_sync as sync_module,
)


class DummyCtx:
    def __init__(self) -> None:
        self.time_zone = "UTC"
        self.warnings: list[str] = []

    def set_warning(self, message: str) -> None:
        self.warnings.append(message)


def _make_stop(
    *,
    stop_id: int,
    client_id: str,
    route_solution_id: int,
    stop_order: int,
    order_id: int | None,
    to_next_polyline: str | None,
):
    return SimpleNamespace(
        id=stop_id,
        client_id=client_id,
        route_solution_id=route_solution_id,
        order_id=order_id,
        service_duration="0",
        in_range=True,
        stop_order=stop_order,
        reason_was_skipped=None,
        has_constraint_violation=False,
        constraint_warnings=None,
        eta_status="valid",
        expected_arrival_time=datetime(2026, 2, 28, 12, 0, 0, tzinfo=timezone.utc),
        actual_arrival_time=None,
        to_next_polyline=to_next_polyline,
    )


def test_plan_change_bundle_includes_synced_old_route_stops(monkeypatch):
    ctx = DummyCtx()
    order = SimpleNamespace(id=500)

    old_plan = SimpleNamespace(id=10, plan_type="local_delivery")
    new_plan = SimpleNamespace(id=99, plan_type="international_shipping")

    predecessor = _make_stop(
        stop_id=11,
        client_id="old_prev",
        route_solution_id=901,
        stop_order=1,
        order_id=111,
        to_next_polyline="old-segment",
    )

    route_solution = SimpleNamespace(
        id=901,
        is_optimized="optimize",
        local_delivery_plan=SimpleNamespace(
            delivery_plan=SimpleNamespace(
                orders=[SimpleNamespace(id=111), SimpleNamespace(id=222)]
            )
        ),
        stops=[predecessor],
        start_leg_polyline="start",
        end_leg_polyline="end",
    )

    old_local_delivery = SimpleNamespace(id=700, delivery_plan_id=old_plan.id)

    apply_context = PlanChangeApplyContext(
        local_delivery_by_plan_id={old_plan.id: old_local_delivery},
        route_solutions_by_local_delivery_id={old_local_delivery.id: [route_solution]},
    )

    monkeypatch.setattr(
        module,
        "remove_order_stops_for_local_delivery",
        lambda order_id, local_delivery_plan_id: ([], [route_solution], {route_solution.id: 1}),
    )

    def _refresh(**kwargs):
        predecessor.to_next_polyline = None
        return [predecessor]

    monkeypatch.setattr(sync_module, "refresh_route_solution_incremental", _refresh)
    monkeypatch.setattr(
        module,
        "serialize_route_solution",
        lambda route_solution: {
            "id": route_solution.id,
            "client_id": "route_901",
            "start_leg_polyline": route_solution.start_leg_polyline,
            "end_leg_polyline": route_solution.end_leg_polyline,
        },
    )

    result = module.apply_local_delivery_plan_change(
        ctx=ctx,
        order_instance=order,
        old_plan=old_plan,
        new_plan=new_plan,
        apply_context=apply_context,
    )

    for action in result.post_flush_actions:
        action()

    bundle = result.serialize_bundle()
    assert "order_stops" in bundle
    assert len(bundle["order_stops"]) == 1
    assert bundle["order_stops"][0]["id"] == 11
    assert bundle["order_stops"][0]["to_next_polyline"] is None
    assert "route_solution" in bundle
    assert len(bundle["route_solution"]) == 1
    assert bundle["route_solution"][0]["id"] == 901
