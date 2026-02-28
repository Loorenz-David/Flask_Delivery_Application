from dataclasses import dataclass

from Delivery_app_BK.errors import ValidationFailed
from Delivery_app_BK.services.domain.item.item_states import ItemStateId
from Delivery_app_BK.services.domain.order.order_states import OrderStateId
from Delivery_app_BK.services.requests.common.datetime import parse_optional_datetime
from Delivery_app_BK.services.requests.common.fields import (
    validate_forbidden,
    validate_unexpected,
)
from Delivery_app_BK.services.requests.common.types import (
    parse_client_id,
    parse_optional_dict,
    parse_optional_int,
    parse_optional_json,
    parse_optional_string,
    parse_required_bool,
    parse_required_int,
    validate_str,
)


ORDER_ALLOWED_FIELDS = {
    "client_id",
    "order_plan_objective",
    "reference_number",
    "external_order_id",
    "external_source",
    "tracking_number",
    "tracking_link",
    "client_first_name",
    "client_last_name",
    "client_email",
    "client_primary_phone",
    "client_secondary_phone",
    "client_address",
    "marketing_messages",
    "earliest_delivery_date",
    "latest_delivery_date",
    "preferred_time_start",
    "preferred_time_end",
    "order_state_id",
    "delivery_plan_id",
    "items",
}

ORDER_FORBIDDEN_FIELDS = {
    "id",
    "team_id",
    "state",
    "state_history",
    "events",
    "order_cases",
    "delivery_plan",
    "team",
}

ITEM_ALLOWED_FIELDS = {
    "client_id",
    "article_number",
    "reference_number",
    "item_type",
    "properties",
    "quantity",
    "item_position_id",
    "item_state_id",
    "page_link",
    "dimension_depth",
    "dimension_height",
    "dimension_width",
    "weight",
}

ITEM_FORBIDDEN_FIELDS = {
    "id",
    "team_id",
    "order_id",
}

ORDER_OPTIONAL_STRING_FIELDS = {
    "order_plan_objective",
    "reference_number",
    "external_order_id",
    "external_source",
    "tracking_number",
    "tracking_link",
    "client_first_name",
    "client_last_name",
    "client_email",
    "preferred_time_start",
    "preferred_time_end",
}

ITEM_OPTIONAL_STRING_FIELDS = {
    "reference_number",
    "item_type",
    "page_link",
}

ITEM_OPTIONAL_INT_FIELDS = {
    "quantity",
    "item_position_id",
    "item_state_id",
    "dimension_depth",
    "dimension_height",
    "dimension_width",
    "weight",
}

ORDER_OBJECTIVES = {
    "local_delivery",
    "international_shipping",
    "store_pickup",
}


@dataclass
class ItemCreateRequest:
    fields: dict


@dataclass
class OrderCreateRequest:
    fields: dict
    items: list[ItemCreateRequest]
    delivery_plan_id: int | None


def parse_create_order_request(raw_fields: dict) -> OrderCreateRequest:
    if not isinstance(raw_fields, dict):
        raise ValidationFailed("Each create payload in 'fields' must be an object.")

    validate_forbidden(
        raw_fields,
        ORDER_FORBIDDEN_FIELDS,
        context_msg="Forbidden fields in order create payload:",
    )
    validate_unexpected(
        raw_fields,
        ORDER_ALLOWED_FIELDS,
        context_msg="Unexpected fields in order create payload:",
    )

    order_fields: dict = {
        "client_id": parse_client_id(raw_fields.get("client_id"), prefix="order"),
        "order_state_id": _parse_order_state_id(raw_fields.get("order_state_id")),
    }

    delivery_plan_id = _parse_delivery_plan_id(raw_fields.get("delivery_plan_id"))
    if delivery_plan_id is not None:
        order_fields["delivery_plan_id"] = delivery_plan_id

    for field in ORDER_OPTIONAL_STRING_FIELDS:
        if field in raw_fields:
            parsed_value = parse_optional_string(
                raw_fields.get(field),
                field=field,
            )
            if field == "order_plan_objective" and parsed_value:
                if parsed_value not in ORDER_OBJECTIVES:
                    raise ValidationFailed(
                        f"Invalid order_plan_objective: {parsed_value}"
                    )
            order_fields[field] = parsed_value

    if "client_primary_phone" in raw_fields:
        order_fields["client_primary_phone"] = parse_optional_dict(
            raw_fields.get("client_primary_phone"),
            field="client_primary_phone",
        )

    if "client_secondary_phone" in raw_fields:
        order_fields["client_secondary_phone"] = parse_optional_dict(
            raw_fields.get("client_secondary_phone"),
            field="client_secondary_phone",
        )

    if "client_address" in raw_fields:
        order_fields["client_address"] = parse_optional_dict(
            raw_fields.get("client_address"),
            field="client_address",
        )

    if "marketing_messages" in raw_fields:
        order_fields["marketing_messages"] = parse_required_bool(
            raw_fields.get("marketing_messages"),
            field="marketing_messages",
        )

    earliest_delivery_date = None
    latest_delivery_date = None

    if "earliest_delivery_date" in raw_fields:
        earliest_delivery_date = parse_optional_datetime(
            raw_fields.get("earliest_delivery_date"),
            field="earliest_delivery_date",
        )
        order_fields["earliest_delivery_date"] = earliest_delivery_date

    if "latest_delivery_date" in raw_fields:
        latest_delivery_date = parse_optional_datetime(
            raw_fields.get("latest_delivery_date"),
            field="latest_delivery_date",
        )
        order_fields["latest_delivery_date"] = latest_delivery_date

    if earliest_delivery_date and latest_delivery_date:
        if latest_delivery_date < earliest_delivery_date:
            raise ValidationFailed(
                "latest_delivery_date cannot be before earliest_delivery_date."
            )

    item_requests = _parse_items(raw_fields)
    return OrderCreateRequest(
        fields=order_fields,
        items=item_requests,
        delivery_plan_id=delivery_plan_id,
    )


def _parse_items(raw_fields: dict) -> list[ItemCreateRequest]:
    if "items" not in raw_fields:
        return []

    items_payload = raw_fields.get("items")
    if not isinstance(items_payload, list):
        raise ValidationFailed("items must be a list of objects.")

    return [_parse_item(item_raw, index) for index, item_raw in enumerate(items_payload)]


def _parse_item(item_raw, index: int) -> ItemCreateRequest:
    if not isinstance(item_raw, dict):
        raise ValidationFailed(f"items[{index}] must be an object.")

    if "order_id" in item_raw:
        raise ValidationFailed("items[].order_id is not allowed in nested order create.")

    validate_forbidden(
        item_raw,
        ITEM_FORBIDDEN_FIELDS,
        context_msg="Forbidden fields in items payload:",
    )
    validate_unexpected(
        item_raw,
        ITEM_ALLOWED_FIELDS,
        context_msg="Unexpected fields in items payload:",
    )

    item_fields: dict = {
        "client_id": parse_client_id(item_raw.get("client_id"), prefix="item"),
        "item_state_id": _parse_item_state_id(item_raw.get("item_state_id")),
        "article_number": validate_str(
            item_raw.get("article_number"),
            field=f"items[{index}].article_number",
        ),
    }

    for field in ITEM_OPTIONAL_STRING_FIELDS:
        if field in item_raw:
            item_fields[field] = parse_optional_string(
                item_raw.get(field),
                field=f"items[{index}].{field}",
            )

    for field in ITEM_OPTIONAL_INT_FIELDS:
        if field in item_raw:
            item_fields[field] = parse_optional_int(
                item_raw.get(field),
                field=f"items[{index}].{field}",
            )

    if "properties" in item_raw:
        item_fields["properties"] = parse_optional_json(
            item_raw.get("properties"),
            field=f"items[{index}].properties",
        )

    return ItemCreateRequest(fields=item_fields)


def _parse_order_state_id(value) -> int:
    if value is None:
        return OrderStateId.DRAFT
    return parse_required_int(value, field="order_state_id")


def _parse_item_state_id(value) -> int:
    if value is None:
        return ItemStateId.OPEN
    return parse_required_int(value, field="item_state_id")


def _parse_delivery_plan_id(value) -> int | None:
    if value is None:
        return None
    return parse_required_int(value, field="delivery_plan_id")
