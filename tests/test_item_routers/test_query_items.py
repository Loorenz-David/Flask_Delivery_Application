import base64
import gzip
import json

import pytest


ITEM_CATEGORY = {"name": "Seating"}
ITEM_TYPE = {"name": "Dining Chair"}
ITEM_PROPERTY = {"name": "Set Of", "value": "4", "field_type": "number-keyboard"}
ITEM_STATE = {"name": "In Transit"}
ITEM_POSITION = {"name": "Aisle 3"}
ITEM_PAYLOAD = {
    "article_number": "ART-001",
    "item_type_id": 1,
    "item_category_id": 1,
    "properties": [1],
    "item_state_id": 1,
    "item_position_id": 1,
}


def decode_response_payload(response_json: dict) -> dict:
    assert response_json["is_compress"] is True
    compressed = base64.b64decode(response_json["data"])
    decompressed = gzip.decompress(compressed).decode("utf-8")
    return json.loads(decompressed)


def seed_item(client) -> None:
    client.post("/item/create_item_category", json=ITEM_CATEGORY)
    client.post("/item/create_item_type", json=ITEM_TYPE)
    client.post("/item/create_item_property", json=ITEM_PROPERTY)
    client.post("/item/create_item_state", json=ITEM_STATE)
    client.post("/item/create_item_position", json=ITEM_POSITION)
    create_res = client.post("/item/create_item", json=ITEM_PAYLOAD)
    assert create_res.status_code == 200


def test_query_item_returns_expected_payload(client):
    seed_item(client)

    query_payload = {
        "query": {
            "article_number": {"operation": "==", "value": ITEM_PAYLOAD["article_number"]}
        },
        "requested_data": ["id", "article_number", "item_type_id"],
    }

    res = client.post("/item/query_item", json=query_payload)
    assert res.status_code == 200
    body = res.get_json()

    unpacked = decode_response_payload(body)
    assert "items" in unpacked
    assert len(unpacked["items"]) == 1

    item_data = unpacked["items"][0]
    assert item_data["article_number"] == ITEM_PAYLOAD["article_number"]
    assert item_data["item_type_id"] == ITEM_PAYLOAD["item_type_id"]
