from Delivery_app_BK.models import Item, ItemState,ItemPosition, ItemProperty
from Delivery_app_BK.models.managers.object_searcher import GetObject
from Delivery_app_BK.models.managers.object_inspector import ColumnInspector
from Delivery_app_BK.models.managers.object_validators import ValueValidator




def service_update_item( data:dict ):

    item_obj:Item = GetObject.get_object( Item,data.get( 'id' ) ) 

    fields:dict = data.get( "fields" )
    for field, value in fields.items():

        column = ColumnInspector( field, Item )
        column_name = column.column_name

        if column_name == 'item_state_id':

            link = item_obj.update_link(
                column = column,
                value = value,
                target_model = ItemState,
                record_column = 'item_state_record'
                )

            if not link:
                raise Exception(f" Something went wrong updating the column item_state_id on model Item")
            
            continue

        if column_name == 'item_position_id':

            link = item_obj.update_link(
                column = column,
                value = value,
                target_model = ItemPosition,
                record_column = 'item_position_record'
            )
            if not link:
                raise Exception(f" Something went wrong updating the column item_position_id on model Item")

            continue
        # updates many to many relationship
        if column_name == "properties":
            link = item_obj.update_link(
                column = column,
                value = value,
                target_model = ItemProperty
            )
            if not link:
                raise Exception(f" Something went wrong updating the column item_position_id on model Item")

            continue

        column_type = column.get_python_type()
        valid_value = ValueValidator.is_valid_value( value, column_type )
        
        setattr( item_obj, column_name, valid_value)
    

    return {'status':'ok','instance':item_obj}