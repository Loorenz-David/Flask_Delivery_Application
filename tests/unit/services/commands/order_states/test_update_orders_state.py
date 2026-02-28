from types import SimpleNamespace

from Delivery_app_BK.services.commands.order.order_states import (
    update_orders_state as module,
)


class _DummyTransaction:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def test_update_orders_state_updates_and_emits(monkeypatch):
    state_instance = SimpleNamespace(id=4, name="Ready")
    order = SimpleNamespace(id=11, team_id=7, order_state_id=2)
    emitted = []

    monkeypatch.setattr(module, "get_instance", lambda ctx, model, value: state_instance)
    monkeypatch.setattr(module, "_resolve_orders", lambda ctx, orders: [order])
    monkeypatch.setattr(module.db.session, "begin", lambda: _DummyTransaction())
    monkeypatch.setattr(
        module,
        "emit_order_events",
        lambda ctx, events: emitted.extend(events),
    )

    updated_orders = module.update_orders_state(
        ctx=SimpleNamespace(),
        orders=11,
        state_id=4,
    )

    assert order.order_state_id == 4
    assert len(updated_orders) == 1
    assert len(emitted) == 2


def test_update_orders_state_skips_unchanged_without_emitting(monkeypatch):
    state_instance = SimpleNamespace(id=4, name="Ready")
    order = SimpleNamespace(id=11, team_id=7, order_state_id=4)
    emitted = []

    monkeypatch.setattr(module, "get_instance", lambda ctx, model, value: state_instance)
    monkeypatch.setattr(module, "_resolve_orders", lambda ctx, orders: [order])
    monkeypatch.setattr(module.db.session, "begin", lambda: _DummyTransaction())
    monkeypatch.setattr(
        module,
        "emit_order_events",
        lambda ctx, events: emitted.extend(events),
    )

    updated_orders = module.update_orders_state(
        ctx=SimpleNamespace(),
        orders=11,
        state_id=4,
    )

    assert updated_orders == []
    assert emitted == []
