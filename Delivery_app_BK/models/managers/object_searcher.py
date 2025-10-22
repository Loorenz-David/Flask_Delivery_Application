from typing import Any, Union
from datetime import date, datetime

from marshmallow import ValidationError

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError, DataError, OperationalError, ProgrammingError, SQLAlchemyError
from sqlalchemy.inspection import inspect
from sqlalchemy import or_, and_
from sqlalchemy import Integer, String, Float, Boolean, Date, DateTime



# Local Imports
from Delivery_app_BK.models import db
from Delivery_app_BK.models.managers.object_validators import ActionValidator, InstanceValidator

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

    def __init__(self, Obj: Any, data: Union[dict], response: Any):
        self.Obj = Obj
        self.response = response
        self.requested_data = self.validate_requested_data( data.get('requested_data', []) )
        self.query_filters = self.validate_query( data.get('query_filters',{}) )

        self.found_objects = None 
        self.unpacked_data = None
   
   

    def build_query(self,query_filters=None):
        try:
            # query object
            query = self.Obj.query
            
            # if there is no passed query query filters it uses the one store in initiation
            if not query_filters:
                query_filters = self.query_filters
            self.validate_query(query_filters)

            # loop over column value pairs modifying the end query 
            for column, op in self.query_filters.items():

                # validates op (operation) if is a dict with required keys
                if not (isinstance(op, dict) and 'operation' in op and 'value' in op):
                    self.response.set_error(
                        message=f"Invalid filter format for column {column}. Expected dict with 'operation' and 'value'.",
                        status=400
                    )
                    return False

                # validates column exist in model
                if not self.has_column(column):
                    self.response.set_error(
                        message=f"Invalid column {column} on table {self.Obj.__tablename__}.",
                        status=400
                    )
                    return False

                # validates the value pass is of same type as column type
                if not self.value_has_valid_format(column, op['value']):
                    self.response.set_error(
                        message=f"Invalid value type for column {column}, column accepts type {inspect(self.Obj).columns[column].type.python_type}.",
                        status=400
                    )
                    return False

                # sets target
                target_column = getattr(self.Obj, column)

                # finds the target operation for query
                query = self.FILTER_MAP[op['operation']](query, target_column, op['value'])

            self.found_objects = query.all()
            return query

        except (IntegrityError, DataError, OperationalError, ProgrammingError) as e:
            self.response.set_error(str(e), status=400)
            return False

        except SQLAlchemyError as e:
            self.response.set_error(f"Database error: {e}", status=500)
            return False

        except Exception as e:
            self.response.set_error(f"Unexpected error: {e}", status=500)
            return False
        

    def unpack(self,requested_data = None):

        # if there is no passed requeted data it uses the one store in initiation
        if not requested_data:
            requested_data = self.requested_data

        if not self.found_objects:
            self.response.set_error("No object found to unpack")
            return False
        
        self.unpacked_data = []
        for obj in self.found_objects:
            self.unpacked_data.append(obj.to_dict(requested_data))
        
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
