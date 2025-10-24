from typing import Any, Optional
from datetime import date, datetime

from marshmallow import ValidationError

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError, DataError, OperationalError, ProgrammingError, SQLAlchemyError
from sqlalchemy.inspection import inspect
from sqlalchemy import or_, and_
from sqlalchemy import Integer, String, Float, Boolean, Date, DateTime
from flask_sqlalchemy.model import Model


# Local Imports
from Delivery_app_BK.models import db
from Delivery_app_BK.models.managers.object_validators import ActionValidator, InstanceValidator
from Delivery_app_BK.routers.utils.response import Response

class ObjectSearcher(ActionValidator):

    FILTER_MAP = {
        '==': lambda query, col, val: query.filter(col == val),
        '!=': lambda query, col, val: query.filter(col != val),
        '>': lambda query, col, val: query.filter(col > val),
        '>=': lambda query, col, val: query.filter(col >= val),
        '<': lambda query, col, val: query.filter(col < val),
        '<=': lambda query, col, val: query.filter(col <= val),
        'in': lambda query, col, val: query.filter(col.in_(val if isinstance(val, list) else [val])),
        'notin': lambda query, col, val: query.filter(~col.in_(val if isinstance(val, list) else [val])),
        'range': lambda query, col, val: query.filter(col.between(val['start'], val['end'])),
        'or': lambda query, col, val: query.filter(or_(*[ObjectSearcher.FILTER_MAP[cond['operation']](query, col, cond['value'])._criterion for cond in val if 'operation' in cond and 'value' in cond])),
        'and': lambda query, col, val: query.filter(and_(*[ObjectSearcher.FILTER_MAP[cond['operation']](query, col, cond['value'])._criterion for cond in val if 'operation' in cond and 'value' in cond])),
        'contains': lambda query, col, val: query.filter(col.contains(val)),
        'contained_by': lambda query, col, val: query.filter(col.contained_by(val)),
        'has_key': lambda query, col, val: query.filter(col.has_key(val)),
        'has_any': lambda query, col, val: query.filter(col.has_any(val)),
        'has_all': lambda query, col, val: query.filter(col.has_all(val)),

        # like  is a partial string macth: is "com%" in "coment". the % is used as a wild card. ilike is case sensitive
        'like': lambda query, col, val: query.filter(col.like(val)),

        # ilike  is a partial string macth: is "com%" in "coment". the % is used as a wild card. ilike is not case sensitive
        'ilike': lambda query, col, val: query.filter(col.ilike(val)), 
    }

    def __init__(
        self,
        Obj: Any,
        query_filters: Optional[dict] = None,
        requested_data: Optional[list] = None,
        response: Optional[Response] = None,
        data: Optional[dict] = None
    ):
        self.response: Response = response or Response()
        self.Obj = Obj
        self.query_filters = query_filters or {}
        self.requested_data = requested_data or []
        self.query = None
        self.found_objects = None
        self.unpacked_data = None
        self.paginated_query = None
        self.order_by_params = None
        self.pagination_params = None

        if data:
            if not isinstance(data, dict):
                raise ValueError("data must be provided as a dictionary.")
            self.query_filters = data.get("query", self.query_filters or {})
            self.requested_data = data.get("requested_data", self.requested_data or [])
            self.order_by_params = data.get("order_by")
            self.pagination_params = data.get("pagination")

        self.requested_data = self.validate_requested_data(self.requested_data)
   
   

    def build_query(self,query_filters=None):
        try:
            # query object
            query = self.Obj.query
            
            # if there is no passed query query filters, it uses the one store in initiation
            filters_to_use = query_filters if query_filters is not None else self.query_filters
            validated_filters = self.validate_query(filters_to_use)
            if validated_filters is None:
                return False
            self.query_filters = validated_filters

            if not self.query_filters:
                self.query = query
                return True

            # loop over column value pairs modifying the end query
            for column, op in self.query_filters.items():
                if not isinstance(op, dict):
                    self.response.set_error(
                        message=f"Invalid filter format for column {column}. Expected dict with 'operation' and 'value'.",
                        status=400
                    )
                    return False

                # validates op (operation) if is a dict with required keys
                if not (isinstance(op, dict) and 'operation' in op and 'value' in op):
                    self.response.set_error(
                        message=f"Invalid filter format for column {column}. Expected dict with 'operation' and 'value'.",
                        status=400
                    )
                    return False

                operation = op['operation']
                value = op['value']

                # validates column exist in model
                if not self.has_column(column):
                    self.response.set_error(
                        message=f"Invalid column {column} on table {self.Obj.__tablename__}.",
                        status=400
                    )
                    return False

                # validates the value pass is of same type as column type
                if not self.value_has_valid_format(column, value, operation):
                    self.response.set_error(
                        message=f"Invalid value type for column {column}, column accepts type {inspect(self.Obj).columns[column].type.python_type}.",
                        status=400
                    )
                    return False

                # sets target
                target_column = getattr(self.Obj, column)

                if operation not in self.FILTER_MAP:
                    self.response.set_error(
                        message=f"Invalid filter operation '{operation}' for column {column}.",
                        status=400
                    )
                    return False

                # finds the target operation for query
                query = self.FILTER_MAP[operation](query, target_column, value)

            self.query = query
            return True

        except (IntegrityError, DataError, OperationalError, ProgrammingError) as e:
            self.response.set_error(str(e), status=400)
            return False

        except SQLAlchemyError as e:
            self.response.set_error(f"Database error: {e}", status=500)
            return False

        except Exception as e:
            self.response.set_error(f"Unexpected error: {e}", status=500)
            return False
    
    def trigger_query(self):
        self.found_objects = self.query.all()
    
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
        
        self.found_objects = self.paginated_query.items

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

    def unpack(self,requested_data = None):

        # if there is no passed requeted data it uses the one store in initiation
        if not requested_data:
            requested_data = self.requested_data

        if not self.found_objects:
            self.response.set_error("No object found to unpack")
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

class GetObject:
    
    @staticmethod
    def get_object(Model,id):
        
        if not InstanceValidator.is_sqlalchemy_instance(Model):
            raise Exception
        
        if InstanceValidator.is_sqlalchemy_instance(id):
            return id
        
        with db.session.no_autoflush:
            object_query = db.session.get(Model,id)
    
        if not object_query:
            raise NoResultFound(f"No {Model.__name__} found with id '{id}'")
        
        return object_query

class FindObjects:

    @staticmethod
    def find_objects(
        response:Response,
        Model:Model,
        incoming_data:dict,
        compress_data = True,
        unpack_data = True
    ):
        
        try:
            incoming_data = incoming_data or {}
            order_by = incoming_data.get('order_by', { "column": "id", "direction": "desc" })
            pagination = incoming_data.get('pagination', None)
            query_filters = incoming_data.get('query', {})
            requested_data = incoming_data.get('requested_data', [])
            searcher = ObjectSearcher(
                Obj=Model, 
                query_filters=query_filters,
                requested_data = requested_data, 
                response=response
            )

            
            # performs the query 
            run_query = searcher.build_query()
            if not run_query:
                return False
            
            if order_by:
                searcher.order_by(order_by)
            
            # if pagination was passed otherwise all results
            if pagination:
                searcher.paginate(pagination)
            else:
                searcher.trigger_query()

            # if request asked for return data
            if unpack_data:
                # unpacks the found object into a dictionary format
                if not searcher.unpack():
                    return False
                # add the unpacked data to the response
                response.set_payload(searcher.unpacked_data)


            # compresses the payload to gzip
            if compress_data:
                response.compress_payload()

            return True

        except ValueError as e:
            response.set_message(f'Something went wrong obtaining for {Model.__tablename__}')
            response.set_error(
                message = str(e),
                status = 400
            )
        except Exception as e:
            response.set_message(f'Something went wrong obtaining data for {Model.__tablename__}')
            response.set_error(
                message = str(e),
                status = 400
            )

        return False
        
