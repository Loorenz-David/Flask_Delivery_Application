from __future__ import annotations

REGISTER_USER_PAYLOAD = [
    {
        "name": "Aurora Rivera",
        "username": "aurora.rivera",
        "email": "ops@aurora.test",
        "password": "Furn1tur3!",
        "phone_number": {"prefix": "+46", "number": "+46737262136"},
        "team": {
            "name": "Aurora Furnishings",
            "missing_to_configure": {
                "warehouses": True,
                "routes": True,
                "notifications": True,
            },
            "subscription": {
                "tier": "pilot",
                "seats": 12,
            },
        },
    },
]

LOGIN_CREDENTIALS = {
    "email": REGISTER_USER_PAYLOAD[0]["email"],
    "password": REGISTER_USER_PAYLOAD[0]["password"],
}

TEAM_NAME = REGISTER_USER_PAYLOAD[0]["team"]["name"]

USER_ROLES = [
    {
        "key": "operations",
        "role": "Operations Lead",
        "permisions": {
            "routes": True,
            "orders": True,
            "notifications": True,
        },
    },
    {
        "key": "driver",
        "role": "Fleet Driver",
        "permisions": {
            "routes": True,
            "orders": False,
            "notifications": False,
        },
    },
]

DRIVER_USERS = [
    {
        "key": "driver_miguel",
        "username": "miguel.alvarez",
        "email": "miguel.alvarez@aurora.test",
        "password": "DriverOne!",
        "phone_number": {"prefix": "+46", "number": "+46737262136"},
    },
    {
        "key": "driver_frida",
        "username": "frida.hansen",
        "email": "frida.hansen@aurora.test",
        "password": "DriverTwo!",
        "phone_number": {"prefix": "+46", "number": "+46737262136"},
    },
    {
        "key": "driver_solveig",
        "username": "solveig.ostergaard",
        "email": "solveig.ostergaard@aurora.test",
        "password": "DriverThree!",
        "phone_number": {"prefix": "+46", "number": "+46737262136"},
    },
]

WAREHOUSES = [
    {
        "name": "Aurora Hub - Downtown",
        "location": {
            "raw_address": "412 Oslo Gate, Oslo, Norway",
            "country": "Norway",
            "city": "Oslo",
            "postal_code": "0152",
            "coordinates": {"lat": 59.9139, "lng": 10.7522},
        },
    },
    {
        "name": "Aurora Hub - Fjordside",
        "location": {
            "raw_address": "9 Fjordveien, Bærum, Norway",
            "country": "Norway",
            "city": "Bærum",
            "postal_code": "1361",
            "coordinates": {"lat": 59.8945, "lng": 10.5464},
        },
    },
]

ITEM_CATEGORIES = [
    {"key": "seating", "name": "Seating"},
    {"key": "dining", "name": "Dining"},
]

ITEM_TYPES = [
    {"name": "Palisade Sectional", "category_key": "seating", "item_category": "Seating"},
    {"name": "Nordic Drift Dining Table", "category_key": "dining", "item_category": "Dining"},
]

ITEM_PROPERTIES = [
    {
        "name": "Fabric Color",
        "field_type": "select",
        "options": [
            {"label": "Fog Grey", "value": "fog-grey"},
            {"label": "Olive Night", "value": "olive-night"},
            {"label": "Deep Sea", "value": "deep-sea"},
        ],
        "required": True,
        "type_names": ["Palisade Sectional"],
    },
    {
        "name": "Wood Finish",
        "field_type": "select",
        "options": [
            {"label": "Natural Oak", "value": "natural-oak"},
            {"label": "Walnut", "value": "walnut"},
            {"label": "Coal Black", "value": "coal-black"},
        ],
        "required": True,
        "type_names": ["Nordic Drift Dining Table"],
    },
]

ITEM_STATES = [
    {
        "name": "Awaiting Pickup",
        "color": "#94a3b8",
        "default": True,
        "priority":0,
        "description": "Item is staged inside the warehouse.",
    },
    {
        "name": "Out for Delivery",
        "color": "#fbbf24",
        "default": False,
        "priority":2,
        "description": "Item left the dock and is inside the truck.",
    },
    {
        "name": "Delivered",
        "color": "#22c55e",
        "default": False,
        "priority":1,
        "description": "Customer confirmed reception.",
    },
    {
        "name": "Fail",
        "color": "#F56B51",
        "default": False,
        "priority":3,
        "description": "Item was now delivered.",
    },
]

ITEM_POSITIONS = [
    {
        "name": "Warehouse Floor",
        "default": True,
        "description": "Waiting batch assignment on the main floor.",
    },
    {
        "name": "Truck 07",
        "default": False,
        "description": "Loaded into the morning truck.",
    },
]

ROUTE_STATES = [
    {"name": "Scheduled", "color": "#2563eb", "default": True},
    {"name": "In Transit", "color": "#f97316", "default": False},
    {"name": "Completed", "color": "#16a34a", "default": False},
]

ROUTES = [
    {
        "label": "Aurora Morning Loop",
        "delivery_date": "2025-03-01T08:00:00",
        "driver_key": "driver_miguel",
        "expected_start_time": "08:00",
        "expected_end_time": "12:30",
        "start_from_warehouse": "Aurora Hub - Downtown",
        "end_from_warehouse": "Aurora Hub - Downtown",
        "using_optimization_indx": 1,
        "route_state": "Scheduled",
        "arrival_time_range": 30,
    },
    {
        "label": "Fjordside Evening Route",
        "delivery_date": "2025-03-01T15:30:00",
        "driver_key": "driver_frida",
        "expected_start_time": "15:30",
        "expected_end_time": "19:00",
        "start_from_warehouse": "Aurora Hub - Fjordside",
        "end_from_warehouse": "Aurora Hub - Fjordside",
        "using_optimization_indx": 2,
        "route_state": "In Transit",
        "arrival_time_range": 30,
    },
]

ORDERS = [
    {
        "route_label": "Aurora Morning Loop",
        "client_first_name": "Jamal ",
        "client_last_name": "Per ",
        "client_email": "jamal.per@example.com",
        "client_primary_phone": {"prefix":'+46',"number":123214},
        "client_secondary_phone": {"prefix":'+50',"number":3214},
        "client_address": {
            "raw_address": "Kirkegata 16, Oslo",
            "city": "Oslo",
            "country": "Norway",
            "postal_code": "0153",
            "coordinates": {"lat": 59.912, "lng": 10.742},
        },
        "client_language": "en",
        "delivery_after": "09:30",
        "delivery_before": "11:00",
        "marketing_messages": False,
        "delivery_items": [
            {
                "article_number": "SOFA-001",
                "item_category": "Seating",
                "item_type": "Palisade Sectional",
                "item_state": "Out for Delivery",
                "item_position": "Truck 07",
                "weight": 120,
                "dimensions": {"length_cm": 250, "width_cm": 95, "height_cm": 78},
                "properties": {"Fabric Color": "Fog Grey"},
            }
        ],
    },
    {
        "route_label": "Fjordside Evening Route",
        "client_first_name": "Ja ",
        "client_last_name": "hok ",
        "client_email": "ja.hok@example.com",
        "client_primary_phone": {"prefix":'+46',"number":123214},
        "client_secondary_phone": {"prefix":'+50',"number":3214},
        "client_address": {
            "raw_address": "Strandveien 44, Lysaker",
            "city": "Bærum",
            "country": "Norway",
            "postal_code": "1366",
            "coordinates": {"lat": 59.9092, "lng": 10.6283},
        },
        "client_language": "no",
        "expected_arrival_time": "18:10",
        "delivery_after": "17:30",
        "delivery_before": "18:30",
        "stop_time": "00:15",
        "marketing_messages": True,
        "delivery_items": [
            {
                "article_number": "TABLE-204",
                "item_category": "Dining",
                "item_type": "Nordic Drift Dining Table",
                "item_state": "Awaiting Pickup",
                "item_position": "Warehouse Floor",
                "weight": 90,
                "dimensions": {"length_cm": 210, "width_cm": 95, "height_cm": 76},
                "properties": {"Wood Finish": "Natural Oak"},
            }
        ],
    },
]

EMAIL_SMTP_CONFIG = {
    "smtp_server": "smtp.aurora-mail.test",
    "smtp_port": 587,
    "smtp_username": "notifications@aurora.test",
    "smtp_password_encrypted": "encrypted-secret",
    "use_tls": True,
    "use_ssl": False,
    "max_per_session": 80,
}

TWILIO_CONFIG = {
    "twilio_sid": "AC1234567890",
    "twilio_token_encrypted": "encrypted-token",
    "sender_number": "+13015550123",
}

MESSAGE_TEMPLATES = [
    {
        "name": "Delivery Reminder",
        "channel": "sms",
        "content": "Hi {client_name}! Your Aurora delivery arrives between {delivery_after} and {delivery_before}. Reply if you need to reschedule.",
    },
    {
        "name": "Thank You Email",
        "channel": "email",
        "content": "Hi {client_name}, thanks for choosing Aurora Furnishings. Let us know how your experience was!",
    },
]
