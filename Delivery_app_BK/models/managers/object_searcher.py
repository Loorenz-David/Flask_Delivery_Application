from typing import Any, Optional, TYPE_CHECKING
from datetime import date, datetime

from marshmallow import ValidationError

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError, DataError, OperationalError, ProgrammingError, SQLAlchemyError
from sqlalchemy.inspection import inspect
from sqlalchemy import or_, and_, cast
from sqlalchemy import Integer, String, Float, Boolean, Date, DateTime
from flask_sqlalchemy.model import Model


# Local Imports
from Delivery_app_BK.models import db
from Delivery_app_BK.models.managers.object_validators import ActionValidator, InstanceValidator
from Delivery_app_BK.services.utils import (
    ensure_instance_in_team,
    model_requires_team,
    require_team_id,
)

if TYPE_CHECKING:
    from Delivery_app_BK.routers.utils.response import Response

"""
ObjectSearcher is an object that builds query filters by giving column targets, value targets
and the operation the filter should perform
"""
class ObjectSearcher(ActionValidator):

    FILTER_MAP = {
        '==': lambda col, val: col == val,
        '!=': lambda col, val: col != val,
        '>': lambda col, val: col > val,
        '>=': lambda col, val: col >= val,
        '<': lambda col, val: col < val,
        '<=': lambda col, val: col <= val,
        'in': lambda col, val: col.in_(val if isinstance(val, list) else [val]),
        'notin': lambda col, val: ~col.in_(val if isinstance(val, list) else [val]),
        'range': lambda col, val: col.between(val['start'], val['end']),
        'contains': lambda col, val: col.contains(val),
        'contained_by': lambda col, val: col.contained_by(val),
        'has_key': lambda col, val: col.has_key(val),
        'has_any': lambda col, val: col.has_any(val),
        'has_all': lambda col, val: col.has_all(val),
        'like': lambda col, val: col.like(val),
        'ilike': lambda col, val: col.ilike(val),
        'json_ilike': lambda col, val: cast(col, String).ilike(val),
    }

    def __init__(
        self,
        Obj: Any,
        query_filters: Optional[dict] = None,
        requested_data: Optional[list] = None,
        response: Optional["Response"] = None,
        data: Optional[dict] = None
    ):
        if response is None:
            from Delivery_app_BK.routers.utils.response import Response as ResponseClass
            self.response = ResponseClass()
        else:
            self.response = response
        self.Obj = Obj
        self.query_filters = query_filters or {}
        self.requested_data = requested_data or []
        self.query = None
        self.found_objects = None
        self.unpacked_data = None
        self.paginated_query = None
        self.order_by_params = None
        self.pagination_params = None
        self.count_of_objects_found = 0

        if data:
            if not isinstance(data, dict):
                raise ValueError("data must be provided as a dictionary.")
            self.query_filters = data.get("query", self.query_filters or {})
            self.requested_data = data.get("requested_data", self.requested_data or [])
            self.order_by_params = data.get("order_by")
            self.pagination_params = data.get("pagination")

        self.requested_data = self.validate_requested_data(self.requested_data)
   
   
    # builds query with the given filters, wrap this call in a try block to get the errors
    def build_query(self,query_filters=None):
        
        # query object
        query = self.Obj.query
        
        # one can overide the store filters when initializing the object by passing query_filters to build_query
        filters_to_use = query_filters if query_filters is not None else self.query_filters

        self.query_filters = self.validate_query(filters_to_use)


        # loop over column, value pairs. each loop adds an _and or an _or filter to the end query
        for column, op in self.query_filters.items():
            if self.is_or_key(column):
                query = self.apply_or_group(query, op)
            else:
                query = self.apply_condition(query, column, op)

        self.query = query
        return True
    
    # joins nested relationships to query
    def join_relationship_to_query(self, query, column_path: str, op: dict):
        """
        Handles relationship traversal like 'client.orders.item_id'.
        Returns (query, target_column)
        """
        path_parts = column_path.split(".")  # e.g. ["client", "orders", "item_id"]
        current_model = self.Obj
        current_query = query

        # iterate over all but the last part (relationships)
        for rel_name in path_parts[:-1]:
            rel_attr = getattr(current_model, rel_name)
            related_model = rel_attr.property.mapper.class_

            # join if not already joined (SQLAlchemy lazy-joins duplicates fine)
            current_query = current_query.join(rel_attr)

            # update model for next step
            current_model = related_model

        # last part is the final column name
        target_col_name = path_parts[-1]
        target_col = getattr(current_model, target_col_name)

        # validate the operation and value
        op = self.validate_query_operation(op, target_col_name)
        value = op["value"]
        self.value_has_valid_format(target_col_name, value)

        return current_query, target_col, op

    def apply_condition(self, query, column, definition):
        query, expression = self.build_condition_expression(query, column, definition)
        if expression is None:
            return query
        return query.filter(expression)

    def build_condition_expression(self, query, column, definition):
        if self.is_or_key(column):
            return self.build_or_group_expression(query, definition)

        query, target_column, op = self.resolve_column_definition(query, column, definition)
        expression = self.build_expression_from_operation(target_column, op)
        return query, expression

    def resolve_column_definition(self, query, column, definition):
        column_name = self.strip_or_prefix(column)
        if isinstance(column_name, str) and '.' in column_name:
            return self.join_relationship_to_query(query, column_name, definition)

        column_name = self.has_column(column_name)
        op = self.validate_query_operation(definition, column_name)
        self.value_has_valid_format(column_name, op['value'])
        target_column = getattr(self.Obj, column_name)
        return query, target_column, op

    def build_expression_from_operation(self, target_column, op):
        operation = op['operation']
        value = op['value']

        if operation == 'or':
            expressions = [
                self.build_expression_from_operation(target_column, condition)
                for condition in value
                if isinstance(condition, dict) and 'operation' in condition and 'value' in condition
            ]
            expressions = [expr for expr in expressions if expr is not None]
            if not expressions:
                return None
            return or_(*expressions)

        if operation == 'and':
            expressions = [
                self.build_expression_from_operation(target_column, condition)
                for condition in value
                if isinstance(condition, dict) and 'operation' in condition and 'value' in condition
            ]
            expressions = [expr for expr in expressions if expr is not None]
            if not expressions:
                return None
            return and_(*expressions)

        builder = self.FILTER_MAP.get(operation)
        if not builder:
            raise ValueError(f"Invalid filter operation in '{operation}' for column.")
        return builder(target_column, value)

    def apply_or_group(self, query, group_definition):
        query, expressions = self.collect_group_expressions(query, group_definition)
        if expressions:
            query = query.filter(or_(*expressions))
        return query

    def build_or_group_expression(self, query, definition):
        query, expressions = self.collect_group_expressions(query, definition)
        if not expressions:
            return query, None
        return query, or_(*expressions)

    def collect_group_expressions(self, query, definition):
        expressions = []
        if isinstance(definition, list):
            for entry in definition:
                query, child_expressions = self.collect_group_expressions(query, entry)
                expressions.extend(child_expressions)
            return query, expressions

        if not isinstance(definition, dict):
            return query, expressions

        for column, nested in definition.items():
            if self.is_or_key(column):
                query, nested_expression = self.build_or_group_expression(query, nested)
                if nested_expression is not None:
                    expressions.append(nested_expression)
            else:
                stripped = self.strip_or_prefix(column)
                query, expression = self.build_condition_expression(query, stripped, nested)
                if expression is not None:
                    expressions.append(expression)

        return query, expressions

    def is_or_key(self, key):
        return isinstance(key, str) and key.startswith('or-')

    def strip_or_prefix(self, key):
        if isinstance(key, str) and key.startswith('or-'):
            return key[3:]
        return key


    # triggers a search on the build query
    def trigger_query(self):
        self.found_objects = self.query.all()
        self.count_of_objects_found = len(self.found_objects)
    
    # triggers a search on the build query with set pagination
    def paginate(self,pagination:dict):
        page = pagination.get('page')
        per_page = pagination.get('per_page')

        if not page:
            raise ValueError(f"missing page for pagination")
        if not per_page:
            raise ValueError(f"missing per_page for pagination")

        self.paginated_query = self.query.paginate(
            page = page,
            per_page = per_page,
            error_out=False
        )

        self.count_of_objects_found = self.paginated_query.total

        self.found_objects = self.paginated_query.items

    # orders items by order_by
    def order_by(self,order_by:dict):
        column_name = order_by.get("column")
        direction = order_by.get("direction", "desc")

        if not column_name:
            raise ValueError("Missing column for ordering.")

        if not self.has_column(column_name):
            raise ValueError ( f"Invalid column '{column_name}' for ordering.")

        column_attr = getattr(self.Obj, column_name)
        if self.query is None:
            self.query = self.Obj.query

        if direction == "asc":
            self.query = self.query.order_by(column_attr.asc())
        else:
            self.query = self.query.order_by(column_attr.desc())

    # unpacks the data with the given client list of columns
    def unpack(self,requested_data = None):

        # if there is no passed requeted data it uses the one store in initiation
        if not requested_data:
            requested_data = self.requested_data

        if not self.found_objects:
            self.response.set_error(
                message = "No object found to unpack",
                status= 200
            )
            return False
        
        unpacked_data = []
        for obj in self.found_objects:
            unpacked_data.append(obj.to_dict(requested_data))
        
        if self.paginated_query:
            self.unpacked_data = {
                "items":unpacked_data,
                "total":self.paginated_query.total,
                "pages":self.paginated_query.pages,
                "current_page":self.paginated_query.page
            }
        else:
            self.unpacked_data = {
                "items":unpacked_data
            }

        return True

    # checks if there is found objects
    def are_items_found(self):
        if self.found_objects:
            return True
        return False


"""
GetObject is an object that queries on a model by id using db.session.get
"""

class GetObject:
    
    @staticmethod
    def get_object(Model,id, identity=None, skip_team_check=False):

        if not InstanceValidator.is_sqlalchemy_instance(Model):
            raise Exception
        
        if InstanceValidator.is_sqlalchemy_instance(id):
            obj = id
            return obj
        else:
            with db.session.no_autoflush:
                object_query = db.session.get(Model,id)
            if not object_query:
                raise NoResultFound(f"No {Model.__name__} found with id '{id}'")
            obj = object_query

        if not skip_team_check:
            if hasattr(obj, "team_id") :
                ensure_instance_in_team(obj, identity)

        return obj


"""
FindObjects is an object that centralizes a query on the database, the client must provide a dictionary as follows
{
    "order_by": { "column": "created_date", direction: "desc" } 
    # order by is optional, by default it will order by latest id with {"column": "id", "direction": "desc" }

    "pagination": { "page": 1, "per_page": 20}
    # pagination is optional, by default no pagination will be implemented, so it will return all query results.

    "requested_data": [ "id", "client_name", {"items": [ "article_number" ] } ]
    # if no requested data the response object will have an empty list but the FindObjects  will return True if items where found

    "query": {
        "client_name": { 
            "value": "%robert%"
            "operation": "ilike"
        },
        "address":{
            "value": "some address 23"
            "operation": "=="
        }
    }
    # is a mandatory key, refer to the documentation to see the types of operations,
    and how to query through relationships,
    if the query dictionary is empty it gets all the objects.
}
"""
class FindObjects:

    @staticmethod
    def find_objects(
        response:"Response",
        Model:Model,
        compress_data = True,
        unpack_data = True,
        identity=None
    ):
        
        try:
            if response.error:
                return False

            identity = identity or getattr(response, "identity", None)

            incoming_data = response.incoming_data
            if incoming_data is None:
                incoming_data = {}
            if not isinstance(incoming_data, dict):
                raise ValueError("Query payload must be provided as a dictionary.")
            
            order_by = incoming_data.get('order_by', { "column": "id", "direction": "desc" })
            pagination = incoming_data.get('pagination', None)
            query_filters = dict(incoming_data.get('query', {}))
            if model_requires_team(Model):
                team_id = require_team_id(identity)
                query_filters.setdefault('team_id', {'operation': '==', 'value': team_id})

            requested_data = incoming_data.get('requested_data', [])
            searcher = ObjectSearcher(
                Obj=Model, 
                query_filters=query_filters,
                requested_data = requested_data, 
                response=response
            )

            
            # performs the query, 
            run_query = searcher.build_query()
            if not run_query:
                return False
            
            if order_by:
                searcher.order_by(order_by)
            
            
            if pagination:
                # restrics the found objects to the page and per_page arguments, stores the items found on self.found_objects
                searcher.paginate(pagination)
            else:
                # stores all found results to self.found_objects
                searcher.trigger_query()

            count_of_objects_found = searcher.count_of_objects_found

            if unpack_data:
                # unpacks the found object into a dictionary format, if no items where found it will not
                # raise an error, but it will set the response error message to "no items found" and return an empty list on key items.
                if not searcher.unpack():
                    response.set_payload({'items':[]})
                    return False
                
                # adds the unpacked data to the response
                response.set_payload(searcher.unpacked_data)
                

            else:
                # checks if items where found with out unpacking
                if not searcher.are_items_found():
                    response.set_payload({'items':[]})
                    response.set_error(
                        message = f"no items found",
                        status = 200
                    )
                    return False
                else:
                    response.set_payload({'items':[]})
                    response.set_error(
                        message = f"items found, but not list of columns was given for unpacking data.",
                        status = 200
                    )
                    
            response.set_message(f"{count_of_objects_found} - Items found")
            
            if compress_data:
                # compresses the payload to gzip
                response.compress_payload()

            return True

        except ValueError as e:
            response.set_message(f'ValueError when querying on table {Model.__tablename__}')
            response.set_error(
                message = str(e),
                status = 400
            )
        except PermissionError as e:
            response.set_message("Unauthorized")
            response.set_error(
                message = str(e),
                status = 403
            )
        except Exception as e:
            response.set_message(f'ExceptionError when querying on table {Model.__tablename__}')
            response.set_error(
                message = str(e),
                status = 400
            )
        except (IntegrityError, DataError, OperationalError, ProgrammingError) as e:
            response.set_message(f'Database Error when querying on {Model.__tablename__}')
            response.set_error(str(e), status=400)
        

        except SQLAlchemyError as e:
            response.set_message(f'Database Error when querying on {Model.__tablename__}')
            response.set_error(str(e), status=500)
            return False



        return False
        
