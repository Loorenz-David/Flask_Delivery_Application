
from  datetime import datetime, timezone

# types
from typing import Type, TYPE_CHECKING


if TYPE_CHECKING:
    from Delivery_app_BK.models.managers.object_inspector import ColumnInspector
    from flask_sqlalchemy.model import Model

class ObjectUpdator:
    
    
    def update_link (
            self,
            column:"ColumnInspector",
            value, 
            target_model:Type["Model"], 
            record_column:str | None =None,
            identity=None
    ):
        from Delivery_app_BK.models.managers.object_linker import ObjectLinker


        self_table = self.__class__
        object_linker = None
        
        if column.is_foreign_key():
            object_linker = ObjectLinker( self, self_table, value, target_model, identity=identity )
            object_linker.link_using_foreign_key( column.column_name)

        elif column.is_relationship():
            
            self.update_relationship_change( column, value, identity=identity )

        else:
            raise ValueError(f"Column '{column.column_name}' is not relatioship or foreign key",
                             f"to model '{target_model.__tablename__}'")

        if record_column:        
            if object_linker is None:
                raise ValueError("Record column tracking is only supported for direct foreign key updates")
            target_label = object_linker.parent.name
            self.update_record(record_column,target_label)
            
            
        return True
   

    def update_record(
            self:"Model", 
            column_name:str, 
            value:str
    ):   
        record_value:list = getattr(self, column_name, None)

        if record_value is None:
            record_value = []

        time = datetime.now(timezone.utc).strftime("%y/%m/%d - %H:%M")
        new_record = {'label': value, 'time':time}
        record_value.append(new_record)

        setattr(self, column_name, record_value)

    def update_relationship_change(
            self,
            column:"ColumnInspector",
            value:list,
            identity=None
    ):
        from Delivery_app_BK.models.managers.object_searcher import GetObject

        # gets the table where the relationship is pointing
        target_model = column.relationship.mapper.class_

        relationship_list:list = getattr(self, column.column_name, None)
        old_ids = []
        new_ids = value
        hash_map_old_rel = {}

        # builds the list of old ids, and the map for later
        for i in range(len(relationship_list)):
            rel_id = relationship_list[i].id
            hash_map_old_rel[rel_id] = i
            old_ids.append(rel_id)

        # gets the difference
        relationships_to_add_ids = self.compare_relationship_change(new_ids, old_ids)
        relationships_to_remove_ids = self.compare_relationship_change(old_ids, new_ids)
        
        # removes the relationships from the difference in O(n)
       
        decrease_by = 0
        for old_id in relationships_to_remove_ids:
            target_i = hash_map_old_rel[old_id]
            target_i -= decrease_by
            last_rel = relationship_list[-1]
            relationship_list[target_i] = last_rel
            relationship_list.pop()
            decrease_by += 1
        
     
        # adds the relationships in O(n)
        for id in relationships_to_add_ids:
            obj_lookup = GetObject.get_object(target_model,id, identity=identity)
            relationship_list.append(obj_lookup)

        setattr(self, column.column_name, relationship_list)

    def compare_relationship_change(self,list_a,list_b):
        return list(set(list_a) - set(list_b))
