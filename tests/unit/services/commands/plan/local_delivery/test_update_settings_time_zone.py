from datetime import datetime, timezone
from types import SimpleNamespace

from Delivery_app_BK.services.commands.plan.local_delivery import (
    update_settings as module,
)


def _make_route_patch():
    return SimpleNamespace(
        route_solution_id=10,
        start_location=None,
        end_location=None,
        set_start_time=None,
        set_end_time=None,
        route_end_strategy=None,
        driver_id=None,
        has_start_location=False,
        has_end_location=False,
        has_set_start_time=False,
        has_set_end_time=False,
        has_route_end_strategy=False,
        has_driver_id=False,
    )


def _make_request(time_zone):
    return SimpleNamespace(
        local_delivery_plan_id=1,
        create_variant_on_save=False,
        time_zone=time_zone,
        delivery_plan=SimpleNamespace(),
        route_solution=_make_route_patch(),
    )


def test_update_local_delivery_settings_uses_identity_timezone_when_missing_in_payload(monkeypatch):
    captured = {}
    now = datetime.now(timezone.utc)
    request = _make_request(time_zone=None)
    delivery_plan = SimpleNamespace(id=2, start_date=now, end_date=now)
    local_delivery_plan = SimpleNamespace(id=1)
    route_solution = SimpleNamespace(id=10, stops=[])

    monkeypatch.setattr(
        module,
        "parse_update_local_delivery_settings_request",
        lambda raw: request,
    )
    monkeypatch.setattr(
        module,
        "load_local_delivery_settings_entities",
        lambda ctx, request: (local_delivery_plan, delivery_plan, route_solution),
    )
    monkeypatch.setattr(
        module,
        "apply_delivery_plan_patch",
        lambda delivery_plan, patch: (delivery_plan.start_date, delivery_plan.end_date, []),
    )

    def _fake_update_route_solution_from_plan(**kwargs):
        captured["time_zone"] = kwargs.get("time_zone")
        return route_solution, False, None

    monkeypatch.setattr(module, "update_route_solution_from_plan", _fake_update_route_solution_from_plan)
    monkeypatch.setattr(module.db.session, "add", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(module.db.session, "add_all", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(module.db.session, "commit", lambda: None)
    monkeypatch.setattr(module, "emit_pending_delivery_plan_events", lambda ctx, events: None)
    monkeypatch.setattr(
        module,
        "build_local_delivery_settings_response",
        lambda ctx, route_solution, stops_changed, route_solution_changed: {},
    )

    module.update_local_delivery_settings(
        SimpleNamespace(
            incoming_data={},
            time_zone="America/New_York",
            set_warning=lambda message: None,
        )
    )

    assert captured["time_zone"] == "America/New_York"


def test_update_local_delivery_settings_uses_context_timezone_even_when_payload_has_timezone(monkeypatch):
    captured = {}
    now = datetime.now(timezone.utc)
    request = _make_request(time_zone="Europe/Stockholm")
    delivery_plan = SimpleNamespace(id=2, start_date=now, end_date=now)
    local_delivery_plan = SimpleNamespace(id=1)
    route_solution = SimpleNamespace(id=10, stops=[])

    monkeypatch.setattr(
        module,
        "parse_update_local_delivery_settings_request",
        lambda raw: request,
    )
    monkeypatch.setattr(
        module,
        "load_local_delivery_settings_entities",
        lambda ctx, request: (local_delivery_plan, delivery_plan, route_solution),
    )
    monkeypatch.setattr(
        module,
        "apply_delivery_plan_patch",
        lambda delivery_plan, patch: (delivery_plan.start_date, delivery_plan.end_date, []),
    )

    def _fake_update_route_solution_from_plan(**kwargs):
        captured["time_zone"] = kwargs.get("time_zone")
        return route_solution, False, None

    monkeypatch.setattr(module, "update_route_solution_from_plan", _fake_update_route_solution_from_plan)
    monkeypatch.setattr(module.db.session, "add", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(module.db.session, "add_all", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(module.db.session, "commit", lambda: None)
    monkeypatch.setattr(module, "emit_pending_delivery_plan_events", lambda ctx, events: None)
    monkeypatch.setattr(
        module,
        "build_local_delivery_settings_response",
        lambda ctx, route_solution, stops_changed, route_solution_changed: {},
    )

    module.update_local_delivery_settings(
        SimpleNamespace(
            incoming_data={},
            time_zone="America/New_York",
            set_warning=lambda message: None,
        )
    )

    assert captured["time_zone"] == "America/New_York"
