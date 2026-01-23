from typing import Dict, Any
from sqlalchemy import and_, or_
from sqlalchemy.orm import Query
from sqlalchemy.orm.attributes import InstrumentedAttribute

from ...utils import to_datetime
from ...context import ServiceContext


def apply_pagination_by_date( 
        query: Query,
        *,
        date_column: InstrumentedAttribute,
        id_column: InstrumentedAttribute,
        params: Dict[str, Any],
        sort: str = 'date_desc'
):
    """
    Assumes the query is already ordered by:
    - date_column ASC/DESC
    - id_column ASC/DESC
    """
    
    # forward pagination
    after_date = params.get("after_date")
    after_id = params.get("after_id")

    # backwards pagination 
    before_date = params.get("before_date")
    before_id = params.get("before_id")

    if after_date and after_id:
        after_date = to_datetime(after_date)
        after_id = int(after_id)

        if sort == 'date_asc':
            query = query.filter(
                or_(
                    date_column > after_date,
                    and_(
                        date_column == after_date,
                        id_column > after_id
                    )
                )
            )

        else:
            query = query.filter(
                    or_(
                        date_column < after_date,
                        and_(
                            date_column == after_date,
                            id_column < after_id
                        )
                    )
                )

    elif before_date and before_id:
    
        before_date = to_datetime(before_date)
        before_id = int(before_id)

        if sort == "date_asc":
            query = query.filter(
                or_(
                    date_column < before_date,
                    and_(
                        date_column == before_date,
                        id_column < before_id
                    )
                )
            )
        else:
            query = query.filter(
                or_(
                    date_column > before_date,
                    and_(
                        date_column == before_date,
                        id_column > before_id
                    )
                )
            )  

    return query 



def is_pagination_backwards( ctx: ServiceContext ):
    return (
        "before_date" in ctx.query_params and
        "before_id" in ctx.query_params
    )

def build_cursor( 
    instance,
    *,
    date_attr,
    id_attr,
    direction = "after",
):
    date_value = getattr( instance, date_attr )
    return {
        f"{direction}_date": date_value.isoformat() if date_value else None,
        f"{direction}_id": getattr( instance, id_attr ),
    }

def build_pagination( 
        page_instances:list, 
        *,
        has_more, 
        date_attr: str,
        id_attr: str,
        ctx: ServiceContext
):
    """
    Builds paginations metadata for cursor-based pagination.

    Assumes:
    - page_instances are already limited
    - query was ordered correctly
    """

    if not page_instances:
        return {
            "has_more": False,
            "next_cursor":None,
            "prev_cursor":None
        }

    if is_pagination_backwards( ctx ):
        page_instances.reverse()
    
    pagination = {
        "has_more": has_more,
        "next_cursor": build_cursor( 
            instance = page_instances[ -1 ], 
            date_attr = date_attr,
            id_attr = id_attr,
            direction = 'after'
        ),
        "prev_cursor": build_cursor( 
            instance = page_instances[ 0 ], 
            date_attr = date_attr,
            id_attr = id_attr,
            direction = 'before'
        ),
    }

    return pagination
