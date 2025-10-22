from typing import Any, Union, Callable
from marshmallow import ValidationError
from Delivery_app_BK.models import db
from sqlalchemy.exc import IntegrityError, DataError, OperationalError, ProgrammingError, SQLAlchemyError
from sqlalchemy.inspection import inspect

from Delivery_app_BK.routers.utils.response import Response


class ObjectCreator:
    @staticmethod
    def create(
        Obj: Any,
        data: Union[dict, list],
        creation_function: Callable[[dict],Any], 
        response: Response, 
        reference: str
    ) -> bool:
        
        
        try:
            # validates that data is a list of dictionaries
            if not isinstance(data,list):
                if isinstance(data,dict):
                    data = [data]
                else:
                    raise ValidationError(f"Data must be in list or dictionary format, instade got: {type(data)}")
            else:
                if len(data) > 0 and not isinstance(data[0],dict):
                    raise ValidationError(f"Data inside the list of dictionary format, instade got: {type(data)}")
            

            # creates object in batch appens to objs list for later commit
            objs = []
            for item in data:
                
                res = creation_function(item)
            
                if res["status"] == 'ok':
                    objs.append(res["instance"])
                
            
            # Bulk or single commit
            if len(objs) > 1:
                db.session.bulk_save_objects(objs)
                db.session.commit()
                response.set_message(f"{len(objs)} {reference}s created successfully")
            else:
                db.session.add(objs[0])
                db.session.commit()
                response.set_message(f"{reference} created successfully")

            return True
        
        except ValueError as e:
            response.set_error(message=str(e), status=400)
            response.set_message("Validation failed")
        except ValidationError as err:
            response.set_error(message=err.messages, status=400)
            response.set_message("Validation failed")
        except IntegrityError as e:
            db.session.rollback()
            response.set_error(message=str(e.orig), status=400)
            response.set_message(f"Integrity error while creating {reference} (e.g., duplicate or FK issue)")
        except DataError as e:
            db.session.rollback()
            response.set_error(message=str(e.orig), status=400)
            response.set_message(f"Invalid data type or value when creating {reference}")
        except OperationalError as e:
            db.session.rollback()
            response.set_error(message=str(e.orig), status=500)
            response.set_message(f"Database operational error while creating {reference}")
        except ProgrammingError as e:
            db.session.rollback()
            response.set_error(message=str(e.orig), status=500)
            response.set_message(f"Database programming error while creating {reference}")
        except SQLAlchemyError as e:
            db.session.rollback()
            message = str(e.orig) if hasattr(e, "orig") else str(e)
            response.set_error(message=message, status=500)
            response.set_message(f"Unexpected SQLAlchemy error while creating {reference}")
        except Exception as e:
            db.session.rollback()
            response.set_error(message=str(e), status=500)
            response.set_message(f"Failed to create {reference}")
        return False