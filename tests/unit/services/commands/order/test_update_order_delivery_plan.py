import pytest

from Delivery_app_BK.errors import ValidationFailed
from Delivery_app_BK.services.commands.order.update_order_delivery_plan import (
    _normalize_order_ids,
)


def test_normalize_order_ids_accepts_single_int():
    assert _normalize_order_ids(5) == [5]


def test_normalize_order_ids_dedupes_list():
    assert _normalize_order_ids([1, 1, 2]) == [1, 2]


def test_normalize_order_ids_rejects_string_ids():
    with pytest.raises(ValidationFailed):
        _normalize_order_ids(["client-1"])  # type: ignore[list-item]
