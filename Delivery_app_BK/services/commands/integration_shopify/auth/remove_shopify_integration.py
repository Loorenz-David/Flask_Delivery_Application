import os
from Delivery_app_BK.errors import NotFound
from Delivery_app_BK.models import db
from Delivery_app_BK.services.queries.integration_shopify import get_integration_by_shop


BACKEND_PUBLIC_URL = os.getenv("BACKEND_PUBLIC_URL")

def handle_shopify_unisntall(shop:str):

    shop_integration = get_integration_by_shop(shop)

    if not shop_integration:
        return

   

    db.session.delete(shop_integration)
    db.session.commit()