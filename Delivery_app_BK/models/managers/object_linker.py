from sqlalchemy.inspection import inspect
from Delivery_app_BK.models import db
from .object_searcher import GetObject
from .object_inspector import ColumnInspector

class ObjectLinker:

    '''
    On initialization the GetObject.get_object makes sure the values assign to child
    and parent are intances by performing a query. if the passed child or parent values are already instances it will just
    return that instance.
    '''
    def __init__(self,child,child_model,parent,parent_model):

        self.child = GetObject.get_object(child_model,child)
        self.child_model = child_model
        self.parent = GetObject.get_object(parent_model,parent)
        self.parent_model = parent_model
    
    def link_using_foreign_key(self,column):

        if not isinstance(column, ColumnInspector):
            column = ColumnInspector(column, self.child_model)

        if not column.is_related_to_model(self.parent_model.__tablename__):
            raise Exception(
                    f"Model {self.child_model.__name__} has no FK relationship to '{self.parent_model.__tablename__}' "
                    f"through column '{column.column_name}'."
                )
        setattr(self.child, column.column_name, self.parent.id)

        return True
    
    def link_using_relationship(self,column):
        if not isinstance(column, ColumnInspector):
            column = ColumnInspector(column, self.child_model)

        if not column.is_relationship():
            raise Exception(
                f"'{column.column_name}' is not a valid relationship on {self.child_model.__name__}"
            )

        attr = getattr(self.child, column.column_name)

        # Many-to-many or one-to-many (uselist=True)
        if column.relationship.uselist:
            if self.parent not in attr:
                attr.append(self.parent)
        else:
            # One-to-one or many-to-one (uselist=False)
            setattr(self.child, column.column_name, self.parent)

        return True