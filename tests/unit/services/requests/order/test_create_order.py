import pytest

from Delivery_app_BK.errors import ValidationFailed
from Delivery_app_BK.services.requests.order.create_order import parse_create_order_request


def test_parse_create_order_accepts_optional_costumer_id_int():
    parsed = parse_create_order_request(
        {
            "client_id": "order_1",
            "costumer_id": 22,
            "client_first_name": "Martha",
        }
    )

    assert parsed.costumer_id == 22
    assert parsed.fields["client_id"] == "order_1"
    assert parsed.fields["client_first_name"] == "Martha"


def test_parse_create_order_rejects_string_costumer_id():
    with pytest.raises(ValidationFailed):
        parse_create_order_request({"costumer_id": "22"})


def test_parse_create_order_rejects_bool_costumer_id():
    with pytest.raises(ValidationFailed):
        parse_create_order_request({"costumer_id": True})


def test_parse_create_order_preserves_existing_fields_behavior():
    parsed = parse_create_order_request(
        {
            "delivery_plan_id": 3,
            "reference_number": "REF-1",
            "order_state_id": 2,
        }
    )

    assert parsed.delivery_plan_id == 3
    assert parsed.costumer_id is None
    assert parsed.fields["delivery_plan_id"] == 3
    assert parsed.fields["reference_number"] == "REF-1"
    assert parsed.fields["order_state_id"] == 2
