from typing import TypeVar

# Third-party dependencies
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()



from .tables.users_models import User
from .tables.items_models import Item
from .tables.items_models import ItemType
from .tables.items_models import ItemCategory
from .tables.items_models import ItemProperty
from .tables.deliveries_models import Order
from .tables.deliveries_models import Route
