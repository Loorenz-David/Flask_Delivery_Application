from types import SimpleNamespace

import Delivery_app_BK.services.commands.order.create_serializers as create_module
import Delivery_app_BK.services.queries.order.serialize_order as list_module


def _build_order_instance():
    return SimpleNamespace(
        id=10,
        client_id="order_10",
        costumer_id=77,
        order_plan_objective=None,
        reference_number="REF-10",
        external_order_id=None,
        external_source=None,
        tracking_number=None,
        tracking_link=None,
        client_first_name="A",
        client_last_name="B",
        client_email="a@mail.com",
        client_primary_phone=None,
        client_secondary_phone=None,
        client_address=None,
        marketing_messages=False,
        earliest_delivery_date=None,
        latest_delivery_date=None,
        preferred_time_start=None,
        preferred_time_end=None,
        creation_date=None,
        order_state_id=1,
        delivery_plan_id=None,
        archive_at=None,
        order_cases=[],
    )


def test_serialize_created_order_includes_costumer_id(monkeypatch):
    monkeypatch.setattr(create_module, "calculate_order_metrics", lambda _order: {})

    serialized = create_module.serialize_created_order(_build_order_instance())

    assert serialized["costumer_id"] == 77


def test_serialize_orders_includes_costumer_id(monkeypatch):
    monkeypatch.setattr(list_module, "calculate_order_metrics", lambda _order: {})
    monkeypatch.setattr(list_module, "map_return_values", lambda values, _ctx, _key: values)

    serialized = list_module.serialize_orders([_build_order_instance()], SimpleNamespace())

    assert serialized[0]["costumer_id"] == 77
