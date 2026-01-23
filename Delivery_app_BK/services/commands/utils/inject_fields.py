from typing import Type
from flask_sqlalchemy.model import Model

from Delivery_app_BK.models import db
from Delivery_app_BK.models.managers.column_inspector import ColumnInspector
from Delivery_app_BK.models.managers.instance_linker import InstanceLinker
from Delivery_app_BK.errors import ValidationFailed, NotFound

from ...context import ServiceContext
from ...queries.get_instance import get_instance


def inject_fields( 
        ctx: ServiceContext,
        instance: Type[ Model ],
        fields: dict,

) -> Type[ Model ]:
    
    if instance is None:
        raise ValidationFailed("instace is required to inject fields to an instance.")
    if fields is None:
        raise ValidationFailed("Fields are required to inject data to an instance.")
    
    Model = instance.__class__

    with db.session.no_autoflush:
        for field, value in fields.items():

            if ctx.skip_id_instance_injection:
                if field == 'id':
                    ctx.set_warning(f'The provided id was ignore because the current context does not allow ID injection')
                    continue
            
            column_inspector = ColumnInspector( field, Model )


            # if the column holds a foreign key, it will link using the foreign key
            if column_inspector.is_foreign_key():

                related_model = (
                    ctx.relationship_map.get( column_inspector.column_name )
                    or column_inspector.get_related_model()
                    )
            
                if related_model is None:
                    raise ValidationFailed(
                        f"Missing relationship mapping for '{column_inspector.column_name}'."
                    )
                if  not value:
                    continue 
                
                related = get_instance( 
                    ctx = ctx,
                    model = related_model,
                    value = value 
                )

                if related is None:
                    raise NotFound(
                        f"Related record for '{column_inspector.column_name}' was not found."
                    )
                
                link = InstanceLinker(
                    owner = instance,
                    related = related,
                ).link_using_foreign_key( column_inspector )
                if not link:
                    raise ValidationFailed(
                        f"Unable to assign '{column_inspector.column_name}' with the provided value."
                    )

                continue
            
            # if the column is a relationship, it will link using relationship_props
            elif column_inspector.is_relationship():
                related_model = (
                    ctx.relationship_map.get( column_inspector.column_name )
                    or column_inspector.get_related_model()
                    )
                if related_model is None:
                    raise ValidationFailed(
                        f"Missing relationship mapping for '{column_inspector.column_name}'."
                    )
                
                # if it's a list (many-to-many) or ( one-to-many )
                if isinstance(value,list):
                    for related_id in value:
                        related = get_instance( 
                            ctx = ctx,
                            model = related_model,
                            value = related_id
                        )

                        if related is None:
                            raise NotFound(
                                f"Related record for '{column_inspector.column_name}' was not found."
                            )

                        link = InstanceLinker(
                            owner = instance,
                            related = related,
                        ).link_using_relationship( column_inspector )
                        if not link:
                            raise ValidationFailed(
                                f"Unable to link '{column_inspector.column_name}' with the provided value."
                            )
                else:
                    # one-to-one or many-to-one
                    related = get_instance( 
                        ctx = ctx,
                        model = related_model,
                        value = value,
                    )
                    if related is None:
                        raise NotFound(
                            f"Related record for '{column_inspector.column_name}' was not found."
                        )
                    link = InstanceLinker(
                            owner = instance,
                            related = related,
                        ).link_using_relationship( column_inspector )
                    if not link:
                        raise ValidationFailed(
                            f"Unable to link '{column_inspector.column_name}' with the provided value."
                        )
                continue




            valid_value = column_inspector.validate_injection( value )

            setattr(instance, column_inspector.column_name, valid_value)

        
    return instance 
