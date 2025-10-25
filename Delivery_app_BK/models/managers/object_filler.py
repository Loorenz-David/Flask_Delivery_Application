from typing import Any, Callable, TYPE_CHECKING
import traceback
from marshmallow import ValidationError

from sqlalchemy.exc import IntegrityError, DataError, OperationalError, ProgrammingError, SQLAlchemyError

from Delivery_app_BK.models import db
from Delivery_app_BK.models.managers.object_validators import DataStructureValidators

if TYPE_CHECKING:
    from Delivery_app_BK.routers.utils.response import Response

action_type_map ={
    'create':['created','creating'],
    'update':['updated','updating'],
    'delete':['deleted','deleting']
}

class ObjectFiller:
    @staticmethod
    def fill_object(
        response: "Response",
        fill_function: Callable[[dict], Any],
        reference: str,
        add_to_session=True,
        action_type='create'
    ) -> bool:
        try:
            if response.error:
                return False

            data = response.incoming_data
            if data is None:
                raise ValueError(f"No data provided for {reference}")

            identity = getattr(response, "identity", None)

            # Initial validation of data structure
            data = DataStructureValidators.is_list_of_dicts(data)

            objs = []
            for object_fields in data:
                
                # if update or create data must have id and fields keys
                if action_type == 'update' or action_type == 'delete':
                    DataStructureValidators.is_valid_update_dict( 
                        data = object_fields,
                        reference = reference, 
                        action_type = action_type
                    )
                
                res = fill_function(object_fields, identity=identity)
                
                if res["status"] == 'ok':
                    if isinstance(res["instance"],list):
                        objs += res["instance"]
                    else:
                        objs.append(res["instance"])
            
            # Bulk or single commit
            if len(objs) > 1:
                if add_to_session:
                    db.session.add_all(objs)
                db.session.commit()
                response.set_message(f"{len(objs)} {reference}s {action_type_map[action_type][0]} successfully")
            else:
                if objs and add_to_session:
                    db.session.add(objs[0])
                db.session.commit()
                response.set_message(f"{reference} {action_type_map[action_type][0]} successfully")

            return True
        
        # Except blocks
        except ValueError as e:
            response.set_error(message=str(e), status=400)
            response.set_message("Validation failed")
        except ValidationError as err:
            response.set_error(message=err.messages, status=400)
            response.set_message("Validation failed")
        except PermissionError as err:
            response.set_error(message=str(err), status=403)
            response.set_message("Unauthorized")
        except IntegrityError as e:
            db.session.rollback()
            response.set_error(message=str(e.orig), status=400)
            response.set_message(f"Integrity error while {action_type_map[action_type][1]} {reference} (e.g., duplicate or FK issue)")
        except DataError as e:
            db.session.rollback()
            response.set_error(message=str(e.orig), status=400)
            response.set_message(f"Invalid data type or value when {action_type_map[action_type][1]} {reference}")
        except OperationalError as e:
            db.session.rollback()
            response.set_error(message=str(e.orig), status=500)
            response.set_message(f"Database operational error while {action_type_map[action_type][1]} {reference}")
        except ProgrammingError as e:
            db.session.rollback()
            response.set_error(message=str(e.orig), status=500)
            response.set_message(f"Database programming error while {action_type_map[action_type][1]} {reference}")
        except SQLAlchemyError as e:
            db.session.rollback()
            message = str(e.orig) if hasattr(e, "orig") else str(e)
            response.set_error(message=message, status=500)
            response.set_message(f"Unexpected SQLAlchemy error while {action_type_map[action_type][1]} {reference}")
        except Exception as e:
            traceback.print_exc()
            db.session.rollback()
            response.set_error(message=str(e), status=500)
            response.set_message(f"Failed to {action_type_map[action_type][0]} {reference}")
            
        return False
    

   
