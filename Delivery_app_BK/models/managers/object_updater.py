
from Delivery_app_BK.models.managers.object_searcher import ObjectSearcher
from sqlalchemy.inspection import inspect

# Local Imports
from Delivery_app_BK.models import db
from Delivery_app_BK.models.managers.object_validators import ActionValidator



# ObjectUpdater class for updating objects dynamically
class ObjectUpdater(ActionValidator):
    def __init__(self, Obj, data, response):
        self.Obj = Obj
        self.response = response
        self.searcher = ObjectSearcher(Obj, data, response)
        self.update_fields = data.get('update_fields', {})

        # Detect relationships in object
        self.relationships = {rel.key: rel.mapper.class_ for rel in inspect(self.Obj).relationships}


    def update(self):
        try:
            query = self.searcher.build_query()
            if query is False:
                return False
            objects = query.all()
            if not objects:
                self.response.set_error("No objects found to update", 404)
                return False
            
            for obj in objects:
                for field, value in self.update_fields.items():
                    if field in self.relationships:
                        self.update_relationship(field,value,obj)

                    elif self.has_column(field):
                        if self.value_has_valid_format(field, value):
                            setattr(obj, field, value)
                        else:
                            continue
                        
            db.session.commit()
            self.response.set_message(f"{len(objects)} object(s) updated successfully")
            return True
        except Exception as e:
            db.session.rollback()
            self.response.set_error(str(e), 500)
            self.response.set_message("Failed to update objects")
            return False
        
    def update_relationship(self, field, value, obj):
        rel_model = self.relationships[field]
        current = getattr(obj, field)

        if isinstance(value, list):
            # Current related IDs
            current_ids = [item.id for item in current] if current is not None else []
            new_ids = value

            # Determine additions and removals
            to_add = set(new_ids) - set(current_ids)
            to_remove = set(current_ids) - set(new_ids)

            # Add new relations
            if to_add:
                add_objs = rel_model.query.filter(rel_model.id.in_(to_add)).all()
                for item in add_objs:
                    if item not in current:
                        current.append(item)

            # Remove outdated relations
            if to_remove:
                remove_objs = rel_model.query.filter(rel_model.id.in_(to_remove)).all()
                for item in remove_objs:
                    if item in current:
                        current.remove(item)

        else:
            # Single relationship assignment
            related = rel_model.query.get(value)
            setattr(obj, field, related)