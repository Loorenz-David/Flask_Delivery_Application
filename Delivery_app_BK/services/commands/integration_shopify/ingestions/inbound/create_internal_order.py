from Delivery_app_BK.errors import NotFound
from Delivery_app_BK.models import ShopifyWebhookEvents
from Delivery_app_BK.services.queries.integration_shopify import get_integration_by_shop
from Delivery_app_BK.services.context import ServiceContext
from Delivery_app_BK.services.commands.order import create_order
from ..mappers import item_mapper, order_mapper

def create_internal_order(
        shop:str,
        payload: dict,
):
        

        shopify_shop = get_integration_by_shop(shop)

        if not shopify_shop:
                raise NotFound(f"Shop integration not found with name: {shop}")
       
        order =  order_mapper(payload)
        
        line_items = payload.get("line_items") or []
        items = [ item_mapper(item) for item in line_items]

        order['items'] = items
        identity = {'team_id': shopify_shop.team_id}

        ctx = ServiceContext(
                incoming_data= { "fields": order },
                identity=identity,
        )

        create_order( ctx )
        
