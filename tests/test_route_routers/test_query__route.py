import base64
import gzip
import json


ROUTE_PAYLOAD = {
    "route_label": "Morning Route",
    "delivery_date": "2025-11-07",
}


def decode_response_payload(response_json: dict) -> dict:
    assert response_json["is_compress"] is True
    compressed = base64.b64decode(response_json["data"])
    decompressed = gzip.decompress(compressed).decode("utf-8")
    return json.loads(decompressed)


def seed_route(client, headers) -> None:
    res = client.post("/route/create_route", json=ROUTE_PAYLOAD, headers=headers)
    assert res.status_code == 200


def test_query_route_returns_results(client, auth_headers):
    seed_route(client, auth_headers)

    query_payload = {
        "query": {
            "route_label": {"operation": "==", "value": ROUTE_PAYLOAD["route_label"]}
        },
        "requested_data": ["id", "route_label"],
    }

    res = client.post("/route/query_route", json=query_payload, headers=auth_headers)
    assert res.status_code == 200
    body = res.get_json()

    unpacked = decode_response_payload(body)
    assert "items" in unpacked
    assert len(unpacked["items"]) == 1
    assert unpacked["items"][0]["route_label"] == ROUTE_PAYLOAD["route_label"]
