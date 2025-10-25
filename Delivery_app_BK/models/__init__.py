from typing import TypeVar

# Third-party dependencies
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()



from .tables.users_models import User
from .tables.users_models import Team
from .tables.users_models import UserRole
from .tables.users_models import UserWarehouse
from .tables.items_models import Item
from .tables.items_models import ItemType
from .tables.items_models import ItemCategory
from .tables.items_models import ItemProperty
from .tables.items_models import ItemState
from .tables.items_models import ItemPosition
from .tables.deliveries_models import Order
from .tables.deliveries_models import Route
from .tables.notifications_models import EmailSMTP
from .tables.notifications_models import TwilioMod
from .tables.notifications_models import MessageTemplate
