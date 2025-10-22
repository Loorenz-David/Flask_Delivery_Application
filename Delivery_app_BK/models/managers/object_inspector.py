from sqlalchemy.inspection import inspect
from .object_validators import InstanceValidator


class ColumnInspector:

    def __init__(self, column, model):
        self.model = None
        self.mapper = None
        self.column = None
        self.column_name = None
        self.column_type = None
        self.relationship_prop = None
        self.relationship = None

        if InstanceValidator.is_sqlalchemy_instance(model):
            self.model = model
            self.mapper = inspect(model)
        else:
            raise ValueError(f"model {model.__name__}, is not an sqlalchemy instance.")

       
        if InstanceValidator.is_sqlalchemy_column(column):
            self.column = column
            self.column_name = column.key

        # if the column is not a Column instance then it must be a string.
        else:
            if not isinstance(column,str):
                raise ValueError(f"column {column}, must be a string or SQLAlchemy Column type")

            self.column_name = column

            # if the given column is a relationship it will get it and skipped the assignment to self.column
            self.relationship = self.get_relationship()
            if not self.is_relationship():
                self.column = self.get_column_instance()
                self.column_type = self.get_python_type()

        


    
    # checks if the column holds any foreign keys
    def is_foreign_key(self):
        if self.column is None:
            return False
        
        return bool(self.column.foreign_keys)

    def is_relationship(self):
        if self.relationship:
            return True
        
        return False

    # chek if the given model holds the relationship to the column
    def is_related_to_model(self,name_of_model_to_check):

        if not self.is_foreign_key():
            return False
        
        # gets the first foreign key
        foreign_key = list(self.column.foreign_keys)[0]
        target_model = foreign_key.column.table

        return target_model.name == name_of_model_to_check

    # obtains the Column object from the model
    def get_column_instance(self):
        mapper = self.mapper 
        column_name = self.column_name
        column = mapper.columns.get( column_name, None )
        if column is not None:
            return column
        
        raise ValueError(f"Column '{column_name}' not found in model '{self.model.__tablename__}' ")

    def get_relationship(self):
        return self.mapper.relationships.get(self.column_name)

    def get_column_type(self):
        return self.column.type
    
    def get_python_type(self):
        try:
            
            return self.column.type.python_type
        except NotImplementedError:
            return object
