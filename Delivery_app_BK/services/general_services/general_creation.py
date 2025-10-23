
# Local Imports 
from Delivery_app_BK.models.managers.object_inspector import ColumnInspector
from Delivery_app_BK.models.managers.object_linker import ObjectLinker
from Delivery_app_BK.models.managers.object_validators import ValueValidator

# import types 
from typing import Type
from flask_sqlalchemy.model import Model




"""
A function design to handle the simple creation of any instance on
SQLAlchmey models
"""

def create_general_object(
    fields: dict,
    Model: Type[Model],
    relationship_map: dict | None = None
) -> dict : 
    
    # Ensure relationship_map is a valid dict
    if relationship_map is None:
        relationship_map = {}
    
    # Creates an instance with the given model
    new_item = Model()
    
    

    for field, value in fields.items():
        
        if field == 'id':
            continue

        column_inspect = ColumnInspector(field,Model)
        
        '''
            if a link will be performed, the ObjectLinker accepts an id (int) or 
            an object instance on child and parent parameters
        '''

        # if the column holds a foreign key, it will link using the foreign key
        if column_inspect.is_foreign_key():
            link = ObjectLinker(
                child = new_item,
                child_model = Model,
                parent = value,
                parent_model = relationship_map.get( column_inspect.column_name )
            ).link_using_foreign_key( column_inspect )
            
            if not link:
                raise Exception (f"something went wrong when assigning {value} to column {column_inspect.column_name}")

            continue
        
        # if the column is a relationship, it will link using relationship_props
        elif column_inspect.is_relationship():
            parent_model = relationship_map.get( column_inspect.column_name )

            # if it's a list (many-to-many)
            if isinstance(value,list):
                for parent_id in value:
                    link = ObjectLinker(
                        child = new_item,
                        child_model = Model,
                        parent = parent_id,
                        parent_model = parent_model
                    ).link_using_relationship( column_inspect )
            else:
                # one-to-one or many-to-one
                link = ObjectLinker(
                        child = new_item,
                        child_model = Model,
                        parent = value,
                        parent_model = parent_model
                    ).link_using_relationship( column_inspect )
            continue

        # if is just a column in the table then a value validation is preform before assigment
        valid_value = ValueValidator.is_valid_value(value,column_inspect.column_type)

        setattr(new_item, column_inspect.column_name, valid_value)
        
   
    
    return {"status":"ok", "instance":new_item}