import pytest
import logging
from tests.test_item_routers.test_create_items import test_item, setup_item_dependencies_creation

@pytest.fixture
def dependencies_for_order(client):
    data = {
        "route_label":"tiptapp",
        "delivery_date":"2025-11-07"
    }
   
    res = client.post("/route/create_route",json=data)
    json_re = res.get_json()
   

def test_create_order(
        client,
        dependencies_for_order,
        caplog,setup_logger,
        setup_item_dependencies_creation
):
    caplog.set_level(logging.DEBUG)
   
    order_data = {
        "route_id":1,
        "client_name":"Robert Jhon",
        "delivery_items":[
            test_item
        ]
    }

    res = client.post("/order/create_order",json=order_data)   
    json_res = res.get_json()
    
   

    assert res.status_code == 200
    assert "Order" in json_res["message"] 