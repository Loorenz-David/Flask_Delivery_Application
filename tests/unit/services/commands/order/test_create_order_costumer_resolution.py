from contextlib import contextmanager
from types import SimpleNamespace

import Delivery_app_BK.services.commands.order.create_order as module
from Delivery_app_BK.services.requests.order.create_order import OrderCreateRequest


@contextmanager
def _tx():
    yield


class _DummySession:
    def __init__(self) -> None:
        self.added: list[object] = []

    def begin(self):
        return _tx()

    def add_all(self, instances):
        self.added.extend(instances)

    def flush(self):
        return None


def _build_request(
    *,
    client_id: str,
    costumer_id: int | None,
    email: str | None = None,
):
    return OrderCreateRequest(
        fields={
            "client_id": client_id,
            "client_first_name": "Name",
            "client_last_name": "Last",
            "client_email": email,
        },
        items=[],
        delivery_plan_id=None,
        costumer_id=costumer_id,
    )


def _patch_create_order_dependencies(monkeypatch, requests):
    dummy_session = _DummySession()
    monkeypatch.setattr(module, "db", SimpleNamespace(session=dummy_session))
    monkeypatch.setattr(module, "extract_fields", lambda _ctx: [{"idx": i} for i in range(len(requests))])
    monkeypatch.setattr(module, "parse_create_order_request", lambda raw: requests[raw["idx"]])
    monkeypatch.setattr(module, "_load_delivery_plans_by_id", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(module, "build_order_created_event", lambda order: {"order_id": order.id})
    monkeypatch.setattr(module, "emit_order_events", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(
        module,
        "serialize_created_order",
        lambda order: {
            "id": order.id,
            "client_id": order.client_id,
            "costumer_id": order.costumer_id,
        },
    )
    monkeypatch.setattr(module, "serialize_created_items", lambda _items: [])

    def _create_instance(_ctx, model, fields):
        if model is module.Order:
            return SimpleNamespace(
                id=len(dummy_session.added) + 1,
                client_id=fields["client_id"],
                items=[],
                delivery_plan_id=None,
                costumer_id=None,
            )
        return SimpleNamespace(client_id=fields.get("client_id", "item"))

    monkeypatch.setattr(module, "create_instance", _create_instance)
    return dummy_session


def test_create_order_links_costumer_ids_in_created_bundles(monkeypatch):
    requests = [
        _build_request(client_id="order_1", costumer_id=None, email="one@mail.com"),
        _build_request(client_id="order_2", costumer_id=None, email="two@mail.com"),
    ]
    _patch_create_order_dependencies(monkeypatch, requests)

    resolver_calls = {"count": 0}

    def _resolve(_ctx, _inputs):
        resolver_calls["count"] += 1
        return [SimpleNamespace(id=101), SimpleNamespace(id=102)]

    monkeypatch.setattr(module, "resolve_or_create_costumers", _resolve)

    result = module.create_order(SimpleNamespace(set_relationship_map=lambda *_args, **_kwargs: None))

    assert resolver_calls["count"] == 1
    assert result["created"][0]["order"]["costumer_id"] == 101
    assert result["created"][1]["order"]["costumer_id"] == 102


def test_create_order_passes_explicit_costumer_id_to_resolver(monkeypatch):
    requests = [_build_request(client_id="order_1", costumer_id=88, email="explicit@mail.com")]
    _patch_create_order_dependencies(monkeypatch, requests)
    captured = {}

    def _resolve(_ctx, inputs):
        captured["inputs"] = inputs
        return [SimpleNamespace(id=88)]

    monkeypatch.setattr(module, "resolve_or_create_costumers", _resolve)

    module.create_order(SimpleNamespace(set_relationship_map=lambda *_args, **_kwargs: None))

    assert captured["inputs"][0].costumer_id == 88
    assert captured["inputs"][0].email == "explicit@mail.com"


def test_create_order_fallback_input_uses_order_snapshot_fields(monkeypatch):
    request = OrderCreateRequest(
        fields={
            "client_id": "order_1",
            "client_first_name": "Martha",
            "client_last_name": "Jensen",
            "client_email": "martha@mail.com",
            "client_primary_phone": {"prefix": "+1", "number": "555"},
            "client_address": {"street_address": "Main 1"},
        },
        items=[],
        delivery_plan_id=None,
        costumer_id=None,
    )
    _patch_create_order_dependencies(monkeypatch, [request])
    captured = {}

    def _resolve(_ctx, inputs):
        captured["input"] = inputs[0]
        return [SimpleNamespace(id=201)]

    monkeypatch.setattr(module, "resolve_or_create_costumers", _resolve)

    module.create_order(SimpleNamespace(set_relationship_map=lambda *_args, **_kwargs: None))

    assert captured["input"].costumer_id is None
    assert captured["input"].first_name == "Martha"
    assert captured["input"].last_name == "Jensen"
    assert captured["input"].email == "martha@mail.com"
    assert captured["input"].primary_phone == {"prefix": "+1", "number": "555"}
    assert captured["input"].address == {"street_address": "Main 1"}


def test_create_order_calls_batch_resolver_once_for_many_orders(monkeypatch):
    requests = [
        _build_request(client_id="order_1", costumer_id=None, email="one@mail.com"),
        _build_request(client_id="order_2", costumer_id=None, email="two@mail.com"),
        _build_request(client_id="order_3", costumer_id=None, email="three@mail.com"),
    ]
    _patch_create_order_dependencies(monkeypatch, requests)
    resolver_calls = {"count": 0}

    def _resolve(_ctx, _inputs):
        resolver_calls["count"] += 1
        return [SimpleNamespace(id=1), SimpleNamespace(id=2), SimpleNamespace(id=3)]

    monkeypatch.setattr(module, "resolve_or_create_costumers", _resolve)

    module.create_order(SimpleNamespace(set_relationship_map=lambda *_args, **_kwargs: None))

    assert resolver_calls["count"] == 1
