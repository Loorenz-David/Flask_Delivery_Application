
from flask_sqlalchemy.model import Model
from typing import Type

from Delivery_app_BK.errors import ValidationFailed

from ...context import ServiceContext
from ...utils import model_requires_team, inject_team_id
from ..utils.inject_fields import inject_fields



def create_instance( 
        ctx: ServiceContext,
        Model: Model,
        fields: dict,
) -> Type[ Model ]:
    if Model is None:
        raise ValidationFailed("Model is required to create an instance.")
    if fields is None:
        raise ValidationFailed("Fields are required to create an instance.")


    if ctx.inject_team_id:
        if model_requires_team( Model ):
            inject_team_id( fields, ctx )

    new_instance = Model()
    from sqlalchemy import inspect

    state = inspect(new_instance)


    inject_fields( 
        ctx,
        new_instance,
        fields
    )
    
    return new_instance
