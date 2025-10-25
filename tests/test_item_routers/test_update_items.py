import pytest
from tests.test_item_routers.test_create_items import setup_item_dependencies_creation, test_item

def test_update_item( client, setup_item_dependencies_creation, auth_headers ):

    item_update = {
        'id':1,
        'fields':{
            'article_number':'1111',
            'item_state_id':2,
            'item_position_id':2,
            'properties':[2]
        }
    }

    item_res = client.post('/item/create_item', json=test_item, headers=auth_headers)

    res = client.put( "/item/update_item", json=item_update, headers=auth_headers )
    res_json = res.get_json()
    assert res.status_code == 200
    assert 'Item' in res_json["message"]
