from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from Delivery_app_BK.routers.utils.role_decorator import role_required


from Delivery_app_BK.models.managers.object_filler import ObjectFiller
from Delivery_app_BK.models.managers.object_searcher import GetObject
from Delivery_app_BK.models import Order, db
from Delivery_app_BK.routers.utils.response import Response
from Delivery_app_BK.services import service_update_order
from . import order_bp


@order_bp.route("/update_order", methods=["PUT"])
@jwt_required()
@role_required([1])
def update_order():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    ObjectFiller.fill_object(
        fill_function=service_update_order,
        response=response,
        reference="Order",
        add_to_session=False,
        action_type="update",
    )

    return response.build()


@order_bp.route("/update_order_chat", methods=["PUT"])
@jwt_required()
@role_required([1, 2, 3])
def update_order_chat():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    if response.error:
        return response.build()

    try:
        data = response.incoming_data or {}
        if not isinstance(data, dict):
            raise ValueError("Payload must be a dictionary.")

        order_id = data.get("id")
        chat = data.get("chat")

        if not isinstance(order_id, int):
            raise ValueError("Order id is required and must be an integer.")
        if not isinstance(chat, dict):
            raise ValueError("Chat payload is required and must be an object.")


        order = GetObject.get_object(Order, order_id, identity=identity)

        current_chat = order.notes_chat if isinstance(order.notes_chat, list) else []
        # copy list to avoid mutating underlying json inadvertently
        updated_chat = list(current_chat)
        updated_chat.append(chat)
        order.notes_chat = updated_chat

        db.session.add(order)
        db.session.commit()

        response.set_message("Chat updated.")
    except Exception as e:
        db.session.rollback()
        response.set_error(str(e), 400)

    return response.build()
