from sqlalchemy.inspection import inspect
from sqlalchemy import Column
from sqlalchemy.orm.attributes import InstrumentedAttribute
from datetime import datetime, timezone

from typing import Any
from sqlalchemy.orm.exc import UnmappedInstanceError
from sqlalchemy.exc import NoInspectionAvailable

class ActionValidator:
     
    def validate_query( 
            self, 
            query_filters:dict
    ):
        if not isinstance( query_filters, dict ):
            raise ValueError("Invalid query_filters format, it must be of type dict as follows:",
                            "Example:",
                            "--> query_filters: {'column': {'value': 'target_value', 'operation': '=='} } <---"
                         )
        elif query_filters is None:
            raise ValueError("Missing query filters, it must be a dict with the columns as keys and a value of type dict with ",
                             "key value and key operation. Example:",
                            "--> query_filters: {'column': {'value': 'target_value', 'operation': '=='} } <---"
                             )
        
        return query_filters
    

    def validate_query_operation( 
            self,
            operation:dict, 
            column:str
    ):
        if not isinstance( operation, dict ):
            raise ValueError(f"Invalid operation format for column {column}. Expected dict with 'operation' and 'value'.",
                            "Example:",
                            "query_filters: {'column': ---> {'value': 'target_value', 'operation': '=='} <--- }"
            )
                
        elif 'operation' not in operation or 'value' not in operation:
            raise ValueError(f"Invalid operation format for column {column}. Expected dict with 'operation' and 'value'.",
                            "Example:",
                            "query_filters: {'column': ---> {'value': 'target_value', 'operation': '=='} <--- }"
            )
        return operation
        

    def validate_requested_data(
            self, 
            requested
    ):
        if isinstance(requested, list):
            return requested
        
        raise ValueError("Invalid requested_data format, it must be of type list")


    def has_column(
            self, 
            column: str
    ) -> bool:
        if not isinstance( column, str ):
            raise ValueError (f"Invalid column type for '{column}' on table {self.Obj.__tablename__}.",
                              "Must be of type str"
                              )

        if not column in inspect( self.Obj ).columns:
            raise ValueError (f"Invalid column {column} on table {self.Obj.__tablename__}.")

        return column


    def value_has_valid_format(
            self, 
            column: str, 
            value: Any
    ) -> bool:
        # allows empty filters
        if value is None:
            return True

        try:
            column_type = inspect(self.Obj).columns[column]
            column_python_type = column_type.type.python_type
        except (KeyError, NotImplementedError, AttributeError):
            # if SQLAlchemy cannot provide the python type, skip strict validation
            return True

        if isinstance(value, (list, tuple, set)):
            return all(isinstance(item, column_python_type) for item in value)

        if isinstance(value, dict):
            # ranges or nested operations are validated elsewhere
            return True

        # check if value and type is the same type
        if isinstance(value, column_python_type):
            return True

        raise ValueError(f"Invalid value type for column '{column}', column accepts type: '{column_python_type}' .")
        
    
class InstanceValidator:

    # Checks if the passed instance is a SQLAlchemy instance
    @staticmethod
    def is_sqlalchemy_instance(obj):
        try:
            inspect(obj)
            return True
        except (UnmappedInstanceError, NoInspectionAvailable):
            return False

    # Checks if the pass object is a SQLAlchemy object
    @staticmethod
    def is_sqlalchemy_column(obj):
        if isinstance(obj, (Column,InstrumentedAttribute)):
            return True
        else:
            return False

class ValueValidator:

    @staticmethod
    def is_valid_value(value,column_type):

        if not column_type:
            raise ValueError(f"No column type was given on is_valid_value")
        
         # Try datetime conversion if type mismatch
        if isinstance(value, str) and column_type is datetime:
            try:
                # Handles both Python and JS ISO formats
                return datetime.fromisoformat(value).replace(tzinfo=timezone.utc)
            except ValueError as e:
                raise e


        if isinstance(value,column_type):
            return value

        
        

        raise Exception(f"the type '{type(value)}' is not supported by column, it must be '{column_type}'")

class DataStructureValidators:

    @staticmethod
    def is_list_of_dicts(data):
        if not isinstance(data,list):
            if isinstance(data,dict):
                data = [data]
            else:
                raise ValueError(f"Data must be in list or dictionary format, instade got: {type(data)}")
        else:
            if len(data) > 0 and not isinstance(data[0],dict):
                raise ValueError(f"Data inside the list of dictionary format, instade got: {type(data)}")
        
        return data
    
    @staticmethod
    def is_valid_update_dict(data:dict, reference,action_type="modify"):
        print("dat in is_valid_dict", data)
        has_id = data.get('id',None)
        has_fields = data.get('fields',None)

        if has_id is None:
            raise ValueError(f"Data is missing an id to find the {reference}")
        
        if has_fields is None:
            raise ValueError(f"Data is missing fields to {action_type} {reference}")
        
        if not isinstance(has_fields,dict):
            raise ValueError(f"Fields must be of type dict, to {action_type} {reference}")

        return True
