from typing import Dict, Any
from sqlalchemy.orm import Query

from Delivery_app_BK.models import db, Order, Item
from Delivery_app_BK.services.utils import inject_team_id, model_requires_team
from sqlalchemy import func, String

from ...context import ServiceContext
from ...utils import to_datetime
from ..utils import apply_pagination_by_date
from ..item.find_items import find_items
from .utils import normalize_phone


def find_orders ( 
        params: Dict[str, Any],
        ctx: ServiceContext ,
        query: Query | None = None
):

    query = query or db.session.query( Order )

    if model_requires_team( Order ) and ctx.inject_team_id:
        params = inject_team_id( params, ctx )
    
    if "team_id" in params:
        query = query.filter( Order.team_id == params.get( "team_id" ) )

    if "external_order_id" in params:
        external_order_id = params.get( "external_order_id" ).strip()
        query = query.filter( Order.external_order_id.ilike( f"{external_order_id}%" ) )

    if "external_source" in params:
        external_source = params.get( "external_source" ).strip()
        query = query.filter( Order.external_source.ilike( f"{external_source}%" ) )

    if "tracking_number" in params:
        tracking_number = params.get( "tracking_number" ).strip()
        query = query.filter( Order.tracking_number.ilike( f"{tracking_number}%" ) )

    if "client_first_name" in params:
        client_first_name = params.get( "client_first_name" ).strip()
        query = query.filter( Order.client_first_name.ilike( f"{client_first_name}%" ) )

    if "client_last_name" in params:
        client_last_name = params.get( "client_last_name" ).strip()
        query = query.filter( Order.client_last_name.ilike( f"{client_last_name}%" ) )

    if "client_email" in params:
        client_email = params.get( "client_email" ).strip()
        query = query.filter( Order.client_email.ilike( f"{client_email}%" ) )

    if "client_address" in params:
        client_address = params.get( "client_address" ).strip()
        query = query.filter(
            func.to_tsvector(
                "simple",
                Order.client_address.cast( String )
            ).op("@@")(
                func.plainto_tsquery( "simple", client_address )
            )
        )
    if "client_phone" in params:
        phone = normalize_phone( params.get( "client_phone" ) )
        query = query.filter(
            Order.client_primary_phone["number"].astext.ilike(f"%{phone}%")
            |
            Order.client_secondary_phone["number"].astext.ilike(f"%{phone}%")
        )
    
    if "earliest_delivery_date" in params:
        earliest_delivery_date = to_datetime( params.get( "earliest_delivery_date" ) )
        query = query.filter( Order.earliest_delivery_date >= earliest_delivery_date)

    if "latest_delivery_date" in params:
        latest_delivery_date = to_datetime ( params.get( "latest_delivery_date" ) )
        query = query.filter( Order.latest_delivery_date <= latest_delivery_date )

    if "creation_date_from" in params:
        creation_date_from = to_datetime( params.get("creation_date_from" ) )
        query = query.filter( Order.creation_date >= creation_date_from )
        
    if "creation_date_to" in params:
        creation_date_to = to_datetime( params.get("creation_date_to" ) )
        query = query.filter( Order.creation_date <= creation_date_to )

    if "order_state_id" in params:
        order_state_ids = params.get( "order_state_id" )
        if not isinstance( order_state_ids, ( list, tuple ) ):
            order_state_ids = [ order_state_ids ] 
            
        query = query.filter( Order.order_state_id.in_( order_state_ids ) )


    #----------------------------------------------------



    #  query on items table -------------------------

    item_params = params.get( "items" )
    if item_params:
        query = query.join( Order.items )
        query = find_items(
            params = item_params,
            ctx = ctx,
            query = query,
        )

    #----------------------------------------------------



    # sort query by date_asc or date_desc -------------------------

    if params.get("sort") == 'date_asc':
        query = query.order_by( 
            Order.earliest_delivery_date.asc(),
            Order.id.asc()
        )
    else:
        query = query.order_by( 
            Order.earliest_delivery_date.desc(),
            Order.id.desc()
        )
    #----------------------------------------------------



    # pagination -------------------------
    query = apply_pagination_by_date(
        query = query,
        date_column = Order.earliest_delivery_date,
        id_column = Order.id,
        params = params,
        sort = params.get( "sort", 'date_desc')
    )

    #----------------------------------------------------

    return query