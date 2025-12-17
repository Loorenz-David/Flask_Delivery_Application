from __future__ import annotations

from typing import Dict, Iterable, List, Mapping, Sequence

from Delivery_app_BK.models import (
    db,
    ItemCategory,
    ItemPosition,
    ItemProperty,
    ItemState,
    ItemType,
    RouteState,
    UserRole,
    UserVehicle,
)
from sqlalchemy.exc import IntegrityError

from Delivery_app_BK.services.item_services.service_create import (
    service_create_item_category,
    service_create_item_position,
    service_create_item_property,
    service_create_item_state,
    service_create_item_type,
)
from Delivery_app_BK.services.routes_services.service_create import service_create_route_state
from Delivery_app_BK.services.user_services import  service_create_user_vehicle

RouteStateSeed = Dict[str, str]
ItemPositionSeed = Dict[str, object]
ItemStateSeed = Dict[str, object]
ItemCategorySeed = Dict[str, object]
ItemTypeSeed = Dict[str, object]
ItemPropertySeed = Dict[str, object]
UserRoleSeed = Dict[str, object]
UserVehicleSeed = Dict[str, object]

ROUTE_STATE_SEEDS: Sequence[RouteStateSeed] = [
    {"name": "standby", "color": "#6b7280"},
    {"name": "progress", "color": "#2563eb"},
    {"name": "completed", "color": "#16a34a"},
]

ITEM_POSITION_SEEDS: Sequence[ItemPositionSeed] = [
    {"name": "in-storage", "default": True, "description": "Item is stored and waiting for handling."},
    {"name": "in-packing", "default": False, "description": "Item is being packed and prepared."},
    {"name": "in-loading dock", "default": False, "description": "Item is staged at the loading dock."},
    {"name": "in-truck", "default": False, "description": "Item is loaded in the truck."},
    {"name": "in-client", "default": False, "description": "Item is with the client."},
]

ITEM_STATE_SEEDS: Sequence[ItemStateSeed] = [
    {
        "name": "standby",
        "default": True,
        "color": "#6b7280",
        "priority": 2,
        "description": "The item is awaiting action before processing begins.",
    },
    {
        "name": "processing",
        "default": False,
        "color": "#2563eb",
        "priority": 3,
        "description": "The item is currently being worked on or prepared.",
    },
    {
        "name": "delivering",
        "default": False,
        "color": "#eab308",
        "priority": 4,
        "description": "The item is en route to its destination.",
    },
    {
        "name": "completed",
        "default": False,
        "color": "#22c55e",
        "priority": 1,
        "description": "The item has successfully reached its final stage.",
    },
    {
        "name": "fail",
        "default": False,
        "color": "#ef4444",
        "priority": 5,
        "description": "The item could not be completed due to an error or issue.",
    },
]

ITEM_CATEGORY_SEEDS: Sequence[ItemCategorySeed] = [
    {
        "name": "General",
        "types": ["General Item", "Miscellaneous Object", "Standard Supply"],
    },
    {
        "name": "Furniture",
        "types": ["Furniture Piece", "Chair / Seating", "Table / Surface"],
    },
    {
        "name": "Electronics",
        "types": ["Electronic Device", "Computer / Laptop", "Phone / Mobile"],
    },
    {
        "name": "Packages",
        "types": ["Box / Package", "Envelope Mailer", "Shipping Crate"],
    },
    {
        "name": "Fragile Goods",
        "types": ["Fragile Item", "Glassware", "Artwork / Frame"],
    },
    {
        "name": "Documents",
        "types": ["Document Envelope", "Legal Paperwork", "Printed Report"],
    },
    {
        "name": "Large Items",
        "types": ["Oversized Equipment", "Machinery Component", "Large Furniture Unit"],
    },
    {
        "name": "Bulk Loads",
        "types": ["Pallet / Bulk Load", "Warehouse Bundle", "Material Stack"],
    },
]

_ALL_TYPE_NAMES: List[str] = [type_name for category in ITEM_CATEGORY_SEEDS for type_name in category["types"]]  # type: ignore

ITEM_PROPERTY_SEEDS: Sequence[ItemPropertySeed] = [
    {
        "name": "Fragile",
        "field_type": "dropdown",
        "options": [
            {"label": "Yes", "value": "yes"},
            {"label": "No", "value": "no"},
        ],
        "required": False,
        "type_names": _ALL_TYPE_NAMES,
    },
    {
        "name": "Stackable",
        "field_type": "dropdown",
        "options": [
            {"label": "Yes", "value": "yes"},
            {"label": "No", "value": "no"},
        ],
        "required": False,
        "type_names": _ALL_TYPE_NAMES,
    },
    {
        "name": "Condition",
        "field_type": "dropdown",
        "options": [
            {"label": "New", "value": "new"},
            {"label": "Used", "value": "used"},
            {"label": "Refurbished", "value": "refurbished"},
            {"label": "Damaged", "value": "damaged"},
        ],
        "required": False,
        "type_names": _ALL_TYPE_NAMES,
    },
    {
        "name": "Orientation Required",
        "field_type": "dropdown",
        "options": [
            {"label": "None", "value": "none"},
            {"label": "Upright", "value": "upright"},
            {"label": "Flat Only", "value": "flat"},
        ],
        "required": False,
        "type_names": [
            "Furniture Piece",
            "Chair / Seating",
            "Table / Surface",
            "Electronic Device",
            "Computer / Laptop",
            "Phone / Mobile",
            "Fragile Item",
            "Glassware",
            "Artwork / Frame",
        ],
    },
    {
        "name": "Reference Number",
        "field_type": "text",
        "required": False,
        "type_names": _ALL_TYPE_NAMES,
    },
    {
        "name": "Warranty",
        "field_type": "text",
        "required": False,
        "type_names": [
            "Electronic Device",
            "Computer / Laptop",
            "Phone / Mobile",
            "Standard Supply",
            "Oversized Equipment",
            "Machinery Component",
        ],
    },
    {
        "name": "Expiration Date",
        "field_type": "text",
        "required": False,
        "type_names": [
            "Standard Supply",
            "Box / Package",
            "Envelope Mailer",
            "Shipping Crate",
            "Pallet / Bulk Load",
            "Warehouse Bundle",
            "Material Stack",
            "Miscellaneous Object",
        ],
    },
]


USER_VEHICLE_SEEDS: Sequence[UserVehicleSeed] = [
    {"name": "Delivery Van", "travel_mode": "DRIVING"},
]


def _create_entities(
    seeds: Iterable[Mapping[str, object]],
    create_fn,
    identity: Mapping[str, object],
) -> List[object]:
    instances: List[object] = []
    for seed in seeds:
        result = create_fn(dict(seed), identity=identity)
        if result.get("status") != "ok":
            raise ValueError(f"Failed to create default object for payload: {seed}")
        instance = result["instance"]
        db.session.add(instance)
        instances.append(instance)
    db.session.flush()
    return instances


def bootstrap_team_defaults(identity: Mapping[str, object]) -> None:
    """
    Seed baseline entities for a freshly registered team. Relies on the provided
    identity (team_id) so the records are properly scoped.
    """
    if not identity or not identity.get("team_id"):
        raise ValueError("A valid team_id is required to bootstrap defaults.")

    try:
        _create_entities(ROUTE_STATE_SEEDS, service_create_route_state, identity)
        _create_entities(ITEM_POSITION_SEEDS, service_create_item_position, identity)
        _create_entities(ITEM_STATE_SEEDS, service_create_item_state, identity)

        category_instances = _create_entities(
            ({"name": seed["name"]} for seed in ITEM_CATEGORY_SEEDS),
            service_create_item_category,
            identity,
        )
        category_lookup = {category.name: category.id for category in category_instances}  # type: ignore

        type_payloads: List[ItemTypeSeed] = []
        for seed in ITEM_CATEGORY_SEEDS:
            category_id = category_lookup.get(seed["name"])  # type: ignore
            if category_id is None:
                raise ValueError(f"Missing category id for {seed['name']}")
            for type_name in seed.get("types", []):
                type_payloads.append({"name": type_name, "item_category_id": category_id})

        type_instances = _create_entities(type_payloads, service_create_item_type, identity)
        type_lookup = {item_type.name: item_type.id for item_type in type_instances}  # type: ignore

        property_payloads: List[ItemPropertySeed] = []
        for prop in ITEM_PROPERTY_SEEDS:
            type_names = prop.get("type_names", [])
            related_type_ids = [type_lookup[name] for name in type_names if name in type_lookup]  # type: ignore
            payload = {
                "name": prop["name"],
                "field_type": prop["field_type"],
                "required": prop.get("required", False),
                "options": prop.get("options"),
                "item_types": related_type_ids,
            }
            property_payloads.append(payload)
        _create_entities(property_payloads, service_create_item_property, identity)

        _create_entities(USER_VEHICLE_SEEDS, service_create_user_vehicle, identity)
    except IntegrityError as err:
        db.session.rollback()
        from Delivery_app_BK.routers.utils.response import Response  # avoid circular import
        readable = Response().get_unique_error_message(err)
        raise ValueError(readable or "Default data already exists for this team") from err
