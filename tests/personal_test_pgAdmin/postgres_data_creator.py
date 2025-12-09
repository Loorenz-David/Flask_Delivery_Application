from __future__ import annotations





from typing import Any, Dict, List, Optional

from Delivery_app_BK import app, db
from Delivery_app_BK.models import (
    EmailSMTP,
    ItemCategory,
    ItemPosition,
    ItemProperty,
    ItemState,
    ItemType,
    MessageTemplate,
    Order,
    Route,
    RouteState,
    Team,
    TwilioMod,
    User,
    UserRole,
    UserWarehouse,
)
from tests.personal_test_pgAdmin.payloads import (
    DRIVER_USERS,
    EMAIL_SMTP_CONFIG,
    ITEM_CATEGORIES,
    ITEM_POSITIONS,
    ITEM_PROPERTIES,
    ITEM_STATES,
    ITEM_TYPES,
    LOGIN_CREDENTIALS,
    MESSAGE_TEMPLATES,
    ORDERS,
    REGISTER_USER_PAYLOAD,
    ROUTES,
    ROUTE_STATES,
    TEAM_NAME,
    TWILIO_CONFIG,
    USER_ROLES,
    WAREHOUSES,
)


def wrap_payload(data: Any) -> Dict[str, Any]:
    return {"data": data, "is_compress": False}


class SeedDataCreator:
    def __init__(self) -> None:
        self.client = app.test_client()
        self.token: Optional[str] = None
        self.team: Optional[Team] = None
        self.role_ids: Dict[str, int] = {}
        self.driver_ids: Dict[str, int] = {}
        self.warehouse_ids: Dict[str, int] = {}
        self.item_category_ids: Dict[str, int] = {}
        self.item_type_ids: Dict[str, int] = {}
        self.item_property_ids: Dict[str, int] = {}
        self.item_state_ids: Dict[str, int] = {}
        self.item_position_ids: Dict[str, int] = {}
        self.route_ids: Dict[str, int] = {}

    def run(self) -> None:
        self.token = self.ensure_admin_user()
        self.team = Team.query.filter_by(name=TEAM_NAME).first()
        if not self.team:
            raise RuntimeError(f"Unable to resolve team '{TEAM_NAME}' in the database.")

        self.route_state_ids = self.seed_route_states()
        self.role_ids = self.seed_user_roles()
        self.driver_ids = self.seed_driver_users()
        self.warehouse_ids = self.seed_user_warehouses()
        self.item_category_ids = self.seed_item_categories()
        self.item_type_ids = self.seed_item_types()
        self.item_property_ids = self.seed_item_properties()
        self.item_state_ids = self.seed_item_states()
        self.item_position_ids = self.seed_item_positions()
        self.route_ids = self.seed_routes()
        self.seed_orders()
        self.seed_notifications()

        print("✅ Test data is ready.")

    # Authentication helpers -------------------------------------------------
    def ensure_admin_user(self) -> str:
        token = self.try_login()
        if token:
            return token

        print("Registering seed administrator...")
        response = self.client.post("/user/register_user", json=wrap_payload(REGISTER_USER_PAYLOAD))
        if response.status_code >= 400:
            raise RuntimeError(f"Failed to register admin user: {response.get_json()}")

        token = self.try_login()
        if not token:
            raise RuntimeError("Registration succeeded but login failed.")

        return token

    def try_login(self) -> Optional[str]:
        response = self.client.post("/auth/login", json=wrap_payload(LOGIN_CREDENTIALS))
        if response.status_code >= 400:
            return None
        payload = response.get_json() or {}
        data = payload.get("data") or {}
        return data.get("access_token")

    def auth_headers(self) -> Dict[str, str]:
        if not self.token:
            raise RuntimeError("No access token available.")
        return {"Authorization": f"Bearer {self.token}"}

    def post_with_token(self, path: str, payload: List[Dict[str, Any]]) -> Dict[str, Any]:
        response = self.client.post(path, json=wrap_payload(payload), headers=self.auth_headers())
        body = response.get_json() or {}
        if response.status_code >= 400:
            error = body.get("error") or body.get("message")
            if error and "duplicate" in error.lower():
                print(f"Skipping creation at {path}; record already exists.")
                return body
            raise RuntimeError(f"Request to {path} failed: {body}")
        return body

    # Seed routines ----------------------------------------------------------
    def seed_user_roles(self) -> Dict[str, int]:
        role_map: Dict[str, int] = {}
        for entry in USER_ROLES:
            record = UserRole.query.filter_by(role=entry["role"]).first()
            if not record:
                payload = [{k: v for k, v in entry.items() if k != "key"}]
                print('before api call', payload)
                self.post_with_token("/user/create_user_role", payload)
                print('after api call')
                record = UserRole.query.filter_by(role=entry["role"]).first()
            if record:
                role_map[entry["key"]] = record.id
        return role_map

    def seed_driver_users(self) -> Dict[str, int]:
        role_id = self.role_ids.get("driver")
        if not role_id:
            raise RuntimeError("Driver role was not created; cannot seed drivers.")

        driver_map: Dict[str, int] = {}
        for entry in DRIVER_USERS:
            record = User.query.filter_by(email=entry["email"]).first()
            if not record:
                payload = [{
                        "username": entry["username"],
                        "email": entry["email"],
                        "password": entry["password"],
                        "role_id": role_id,
                        "phone_number": entry.get("phone_number"),
                    }]
                self.post_with_token("/user/create_user", payload)
                record = User.query.filter_by(email=entry["email"]).first()
            if record:
                driver_map[entry["key"]] = record.id
        return driver_map

    def seed_user_warehouses(self) -> Dict[str, int]:
        warehouse_map: Dict[str, int] = {}
        for entry in WAREHOUSES:
            record = UserWarehouse.query.filter_by(name=entry["name"]).first()
            if not record:
                self.post_with_token("/user/create_user_warehouse", [entry])
                record = UserWarehouse.query.filter_by(name=entry["name"]).first()
            if record:
                warehouse_map[entry["name"]] = record.id
        return warehouse_map

    def seed_route_states(self) -> Dict[str, int]:
        state_map: Dict[str, int] = {}
        created = 0
        for entry in ROUTE_STATES:
            record = RouteState.query.filter_by(name=entry["name"], team_id=self.team.id if self.team else None).first()
            if record:
                state_map[entry["name"]] = record.id
                continue
            new_state = RouteState(name=entry["name"])
            if hasattr(new_state, "team_id") and self.team:
                new_state.team_id = self.team.id
            db.session.add(new_state)
            created += 1
        if created:
            db.session.commit()
        for entry in ROUTE_STATES:
            record = RouteState.query.filter_by(name=entry["name"], team_id=self.team.id if self.team else None).first()
            if record:
                state_map[entry["name"]] = record.id
        print(f"Created {created} route states")
        return state_map

    def seed_item_categories(self) -> Dict[str, int]:
        category_map: Dict[str, int] = {}
        for entry in ITEM_CATEGORIES:
            name = entry["name"]
            record = ItemCategory.query.filter_by(name=name).first()
            if not record:
                self.post_with_token("/item/create_item_category", [{"name": name}])
                record = ItemCategory.query.filter_by(name=name).first()
            if record:
                key = entry.get("key") or name
                category_map[key] = record.id
                category_map[name] = record.id
        return category_map

    def seed_item_types(self) -> Dict[str, int]:
        type_map: Dict[str, int] = {}
        for entry in ITEM_TYPES:
            record = ItemType.query.filter_by(name=entry["name"]).first()
            if not record:
                payload = {"name": entry["name"]}
                category_key = entry.get("category_key") or entry.get("item_category")
                if category_key:
                    category_id = self.item_category_ids.get(category_key)
                else:
                    category_id = None
                if not category_id:
                    print(f"Skipping item type '{entry['name']}' because category '{category_key}' is missing.")
                    continue
                payload["item_category_id"] = category_id
                print(payload,' the payload in item type ')
                self.post_with_token("/item/create_item_type", [payload])
                record = ItemType.query.filter_by(name=entry["name"]).first()
            if record:
                type_map[entry["name"]] = record.id
        return type_map

    def seed_item_properties(self) -> Dict[str, int]:
        property_map: Dict[str, int] = {}
        for entry in ITEM_PROPERTIES:
            record = ItemProperty.query.filter_by(name=entry["name"]).first()
            if record:
                property_map[entry["name"]] = record.id
                continue

            type_names = entry.get("type_names", [])
            type_ids = [self.item_type_ids[name] for name in type_names if name in self.item_type_ids]
            payload = {
                "name": entry["name"],
                "field_type": entry["field_type"],
                "options": entry["options"],
                "required": entry["required"],
            }
            if type_ids:
                payload["item_types"] = type_ids

            self.post_with_token("/item/create_item_property", [payload])
            record = ItemProperty.query.filter_by(name=entry["name"]).first()
            if record:
                property_map[entry["name"]] = record.id
        return property_map

    def seed_item_states(self) -> Dict[str, int]:
        state_map: Dict[str, int] = {}
        for entry in ITEM_STATES:
            record = ItemState.query.filter_by(name=entry["name"]).first()
            if not record:
                payload = {
                    "name": entry["name"],
                    "color": entry["color"],
                    "default": entry["default"],
                    "priority":entry["priority"],
                    "description": entry["description"],
                }
                self.post_with_token("/item/create_item_state", [payload])
                record = ItemState.query.filter_by(name=entry["name"]).first()
            if record:
                state_map[entry["name"]] = record.id
        return state_map

    def seed_item_positions(self) -> Dict[str, int]:
        position_map: Dict[str, int] = {}
        for entry in ITEM_POSITIONS:
            record = ItemPosition.query.filter_by(name=entry["name"]).first()
            if not record:
                self.post_with_token("/item/create_item_position", [entry])
                record = ItemPosition.query.filter_by(name=entry["name"]).first()
            if record:
                position_map[entry["name"]] = record.id
        return position_map

    def seed_routes(self) -> Dict[str, int]:
        route_map: Dict[str, int] = {}
        for entry in ROUTES:
            record = Route.query.filter_by(route_label=entry["label"]).first()
            if record:
                route_map[entry["label"]] = record.id
                continue

            driver_id = self.driver_ids.get(entry["driver_key"])
            if not driver_id:
                print(f"Skipping route '{entry['label']}' because driver {entry['driver_key']} is missing.")
                continue

            payload = {
                "route_label": entry["label"],
                "delivery_date": entry["delivery_date"],
                "driver_id": driver_id,
                "expected_start_time": entry.get("expected_start_time"),
                "expected_end_time": entry.get("expected_end_time"),
                "using_optimization_indx": entry.get("using_optimization_indx"),
                "arrival_time_range": entry.get("arrival_time_range", 30),
            }
            route_state_name = entry.get("route_state")
            if route_state_name:
                state_id = self.route_state_ids.get(route_state_name)
                if state_id:
                    payload["state_id"] = state_id

            start_name = entry.get("start_from_warehouse")
            end_name = entry.get("end_from_warehouse")
            start_location = entry.get("start_location")
            end_location = entry.get("end_location")

            if not start_location and start_name:
                warehouse = next((w for w in WAREHOUSES if w["name"] == start_name), None)
                start_location = warehouse["location"] if warehouse else None
            if not end_location and end_name:
                warehouse = next((w for w in WAREHOUSES if w["name"] == end_name), None)
                end_location = warehouse["location"] if warehouse else None

            if start_location:
                payload["start_location"] = start_location
            if end_location:
                payload["end_location"] = end_location

            self.post_with_token("/route/create_route", [payload])
            record = Route.query.filter_by(route_label=entry["label"]).first()
            if record:
                route_map[entry["label"]] = record.id
        return route_map

    def seed_orders(self) -> None:
        for entry in ORDERS:
            route_id = self.route_ids.get(entry["route_label"])
            if not route_id:
                print(f"Skipping order for {entry['client_first_name']}—route '{entry['route_label']}' missing.")
                continue

            existing = (
                Order.query.filter_by(client_first_name=entry["client_first_name"], route_id=route_id).first()
            )
            if existing:
                continue

            delivery_items = []
            for item in entry["delivery_items"]:
                try:
                    delivery_items.append(
                        {
                            "article_number": item["article_number"],
                            "item_category": item["item_category"],
                            "item_type": item["item_type"],
                            "item_state_id": self.item_state_ids[item["item_state"]],
                            "item_position_id": self.item_position_ids[item["item_position"]],
                            "weight": item.get("weight"),
                            "dimensions": item.get("dimensions"),
                            "properties": item.get("properties"),

                        }
                    )
                except KeyError as error:
                    print(f"Unable to create item '{item['article_number']}': missing mapping {error}.")

            if not delivery_items:
                print(f"Skipping order for {entry['client_first_name']} because no items are valid.")
                continue

            payload = {
                "client_first_name": entry["client_first_name"],
                "client_last_name": entry["client_last_name"],
                "client_primary_phone": entry[ "client_primary_phone"],
                "client_email":entry["client_email"],
                "client_secondary_phone": entry.get("client_secondary_phone",''),
                "client_address": entry["client_address"],
                "client_language": entry.get("client_language",''), 
                "expected_arrival_time": entry.get("expected_arrival_time",''),
                "delivery_after": entry.get("delivery_after",''),
                "delivery_before": entry.get("delivery_before",''),
                "stop_time": entry.get("stop_time",''),
                "marketing_messages": entry.get("marketing_messages", False),
                "delivery_items": delivery_items,
                "route_id": route_id,
            }

            self.post_with_token("/order/create_order", [payload])

    def seed_notifications(self) -> None:
        if not EmailSMTP.query.filter_by(smtp_username=EMAIL_SMTP_CONFIG["smtp_username"]).first():
            self.post_with_token("/notifications/create_email_smtp", [EMAIL_SMTP_CONFIG])

        if not TwilioMod.query.filter_by(twilio_sid=TWILIO_CONFIG["twilio_sid"]).first():
            self.post_with_token("/notifications/create_twilio_mod", [TWILIO_CONFIG])

        for entry in MESSAGE_TEMPLATES:
            record = MessageTemplate.query.filter_by(name=entry["name"]).first()
            if not record:
                self.post_with_token("/notifications/create_message_template", [entry])


def run_mock_data() -> None:
    with app.app_context():
        print("Starting seed run…", flush=True)
        creator = SeedDataCreator()
        creator.run()
        print("Seed run finished.")

if __name__ == "__main__":
    run_mock_data()
