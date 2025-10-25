import base64
import gzip
import json

from Delivery_app_BK.models import Team, User, UserRole, UserWarehouse


def compress_payload(payload: dict) -> dict:
    compressed = gzip.compress(json.dumps(payload).encode("utf-8"))
    return {"is_compress": True, "data": base64.b64encode(compressed).decode("utf-8")}


def decode_response_payload(response_json: dict) -> dict:
    assert response_json["is_compress"] is True
    compressed = base64.b64decode(response_json["data"])
    return json.loads(gzip.decompress(compressed).decode("utf-8"))


def seed_user_role(client, app, headers, role_name: str = "Admin") -> UserRole:
    res = client.post(
        "/user/create_user_role",
        json={"role": role_name, "permisions": {"can_manage": True}},
        headers=headers,
    )
    assert res.status_code == 200
    with app.app_context():
        role = UserRole.query.filter_by(role=role_name).first()
        assert role is not None
        return role


def seed_user(client, app, headers, role: UserRole, email: str = "alice@example.com") -> User:
    res = client.post(
        "/user/create_user",
        json={
            "username": "alice",
            "email": email,
            "password": "secret",
            "role_id": role.id,
        },
        headers=headers,
    )
    assert res.status_code == 200
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        assert user is not None
        return user


def seed_user_warehouse(client, app, headers, name: str = "Warehouse Alpha") -> UserWarehouse:
    res = client.post(
        "/user/create_user_warehouse",
        json={
            "name": name,
            "location": {"city": "Quito"},
        },
        headers=headers,
    )
    assert res.status_code == 200
    with app.app_context():
        warehouse = UserWarehouse.query.filter_by(name=name).first()
        assert warehouse is not None
        return warehouse


def test_create_user_resources(client, app, auth_headers):
    role = seed_user_role(client, app, auth_headers)
    warehouse = seed_user_warehouse(client, app, auth_headers)
    user = seed_user(client, app, auth_headers, role)

    with app.app_context():
        assert Team.query.count() == 1
        assert UserRole.query.count() == 1
        assert UserWarehouse.query.count() == 1
        created_user = User.query.filter_by(id=user.id).first()
        assert created_user is not None
        assert created_user.username == "alice"


def test_update_user_via_route(client, app, auth_headers):
    role = seed_user_role(client, app, auth_headers)
    user = seed_user(client, app, auth_headers, role)

    update_payload = {
        "id": user.id,
        "fields": {
            "username": "alice-updated",
            "email": "alice-updated@example.com",
        },
    }

    res = client.put("/user/update_user", json=update_payload, headers=auth_headers)
    assert res.status_code == 200
    assert "User updated successfully" in res.get_json()["message"]

    with app.app_context():
        updated_user = User.query.get(user.id)
        assert updated_user.username == "alice-updated"
        assert updated_user.email == "alice-updated@example.com"


def test_query_user_supports_compressed_payload(client, app, auth_headers):
    role = seed_user_role(client, app, auth_headers)
    seed_user(client, app, auth_headers, role, email="search@example.com")

    query_payload = {
        "query": {
            "email": {"operation": "==", "value": "search@example.com"}
        },
        "requested_data": ["id", "email", "username"],
    }

    res = client.post("/user/query_user", json=compress_payload(query_payload), headers=auth_headers)
    assert res.status_code == 200

    body = res.get_json()
    unpacked = decode_response_payload(body)
    assert "items" in unpacked
    assert len(unpacked["items"]) == 1
    assert unpacked["items"][0]["email"] == "search@example.com"
