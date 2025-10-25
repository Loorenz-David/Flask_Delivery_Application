import base64
import gzip
import json


ITEM_CATEGORY = {"name": "Seating"}
ITEM_TYPE = {"name": "Dining Chair"}
ITEM_PROPERTY = {"name": "Set Of", "value": "4", "field_type": "number-keyboard"}
ITEM_STATE = {"name": "In Transit"}
ITEM_POSITION = {"name": "Aisle 3"}

ROUTE_PAYLOAD = {
    "route_label": "Evening Route",
    "delivery_date": "2025-11-08",
}

CLIENT_NAME = "Test Client"


def decode_response_payload(response_json: dict) -> dict:
    assert response_json["is_compress"] is True
    compressed = base64.b64decode(response_json["data"])
    decompressed = gzip.decompress(compressed).decode("utf-8")
    return json.loads(decompressed)


def build_item_payload(article_number: str) -> dict:
    return {
        "article_number": article_number,
        "item_type_id": 1,
        "item_category_id": 1,
        "properties": [1],
        "item_state_id": 1,
        "item_position_id": 1,
    }


def seed_order(client, headers) -> str:
    # Item dependencies
    client.post("/item/create_item_category", json=ITEM_CATEGORY, headers=headers)
    client.post("/item/create_item_type", json=ITEM_TYPE, headers=headers)
    client.post("/item/create_item_property", json=ITEM_PROPERTY, headers=headers)
    client.post("/item/create_item_state", json=ITEM_STATE, headers=headers)
    client.post("/item/create_item_position", json=ITEM_POSITION, headers=headers)

    # Route dependencies
    route_res = client.post("/route/create_route", json=ROUTE_PAYLOAD, headers=headers)
    assert route_res.status_code == 200

    order_payload = {
        "route_id": 1,
        "client_name": CLIENT_NAME,
        "delivery_items": [build_item_payload("ART-100")],
    }

    res = client.post("/order/create_order", json=order_payload, headers=headers)
    assert res.status_code == 200
    return order_payload["delivery_items"][0]["article_number"]


def test_query_order_returns_results_with_nested_items(client, auth_headers):
    article_number = seed_order(client, auth_headers)

    query_payload = {
        "query": {"client_name": {"operation": "==", "value": CLIENT_NAME}},
        "requested_data": [
            "id",
            "client_name",
            {"delivery_items": ["article_number"]},
        ],
    }

    res = client.post("/order/query_order", json=query_payload, headers=auth_headers)
    body = res.get_json()
    assert res.status_code == 200
    

    unpacked = decode_response_payload(body)
    assert "items" in unpacked
    assert len(unpacked["items"]) == 1

    order_data = unpacked["items"][0]
    assert order_data["client_name"] == CLIENT_NAME
    assert order_data["delivery_items"][0]["article_number"] == article_number
