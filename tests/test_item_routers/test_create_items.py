import pytest
import logging


test_category ={"data": {"name": "Seating"}}
test_type ={"data": {"name": "Dining Chair"}}
test_properties ={"data": {"name": "Set Of", "value": "4", "field_type":"number-keyboard"}}
test_state ={"data": {"name": "In Transit"}}
test_position ={"data": {"name": "Aisle 3"}}
test_item ={"data": {
        'article_number': '030303',
        'item_type_id': 1,
        'item_category_id':1,
        'properties':[1],
        'item_state_id':1,
        'item_position_id':1
    }}

# CREATE ItemState Instance
def test_create_item_state(client, auth_headers):
    res = client.post("/item/create_item_state", json=test_state, headers=auth_headers)

    assert res.status_code == 200
    assert 'Item State' in res.get_json()['message']


# CREATE ItemPosition Instance
def test_create_item_position(client, auth_headers):
    res = client.post("/item/create_item_position", json=test_position, headers=auth_headers)

    assert res.status_code == 200
    assert 'Item Position' in res.get_json()['message']


# CREAT ItemType Instance
def test_create_item_type(client, auth_headers):
    res = client.post("/item/create_item_type",json= test_type, headers=auth_headers)

    assert res.status_code == 200
    assert 'Item Type' in res.get_json()['message']

# CREATE ItemProperty Instance
def test_create_item_porperties(client, auth_headers):
    res = client.post("/item/create_item_property",json= test_properties, headers=auth_headers)

    assert res.status_code == 200
    assert 'Item Property' in res.get_json()['message']

# Create ItemCategory Instance
def test_create_item_category(client, auth_headers):
   
    # Test the category creation route.
    res = client.post("/item/create_item_category",json=test_category, headers=auth_headers)
   
    assert res.status_code == 200
    assert 'Item Category' in res.get_json()["message"]

# Sets up dependencies for the functions test_create_item
@pytest.fixture
def setup_item_dependencies_creation(client, auth_headers):

    client.post('/item/create_item_category', json= test_category, headers=auth_headers)
    client.post('/item/create_item_type', json= test_type, headers=auth_headers)
    client.post('/item/create_item_property', json= test_properties, headers=auth_headers)
    client.post('/item/create_item_property', json= test_properties, headers=auth_headers)

    client.post('/item/create_item_state', json= test_state, headers=auth_headers)
    client.post('/item/create_item_position', json= test_position, headers=auth_headers)
    client.post('/item/create_item_state', json= test_state, headers=auth_headers)
    client.post('/item/create_item_position', json= test_position, headers=auth_headers)

    

# Create Item Instance
def test_create_item(client, setup_item_dependencies_creation,caplog, auth_headers):
    caplog.set_level(logging.DEBUG)
    res = client.post('/item/create_item',json=test_item, headers=auth_headers)

    assert res.status_code == 200
    assert 'Item' in res.get_json()['message']
    
