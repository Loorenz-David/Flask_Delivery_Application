import pytest


def test_create_route(client, auth_headers):

    data = {
        "route_label":"tiptapp",
        "delivery_date":"2025-11-07"
    }

    res = client.post("/route/create_route",json=data, headers=auth_headers)
    json_re = res.get_json()

    
    assert res.status_code == 200
    assert "Route" in json_re["message"] 
