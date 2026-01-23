from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt

from Delivery_app_BK.routers.utils.role_decorator import (
    role_required,
    ADMIN,
    ASSISTANT,
    DRIVER,
)
from Delivery_app_BK.routers.http.response import Response
from Delivery_app_BK.services.context import ServiceContext
from Delivery_app_BK.services.run_service import run_service
from Delivery_app_BK.services.queries.notifications.order.list_order_chats import (
    list_order_chats as list_order_chats_service,
)
from Delivery_app_BK.services.queries.notifications.order.get_order_chat import (
    get_order_chat as get_order_chat_service,
)
from Delivery_app_BK.services.queries.notifications.order.list_unseen_order_chats import (
    list_unseen_order_chats as list_unseen_order_chats_service,
)
from Delivery_app_BK.services.commands.notifications.create_order_chat import (
    create_order_chat as create_order_chat_service,
)
from Delivery_app_BK.services.commands.notifications.update_order_chat import (
    update_order_chat as update_order_chat_service,
)
from Delivery_app_BK.services.commands.notifications.delete_order_chat import (
    delete_order_chat as delete_order_chat_service,
)
from Delivery_app_BK.services.commands.notifications.create_notification_read import (
    create_notification_read as create_notification_read_service,
)


notification_bp = Blueprint("api_v2_notification_bp", __name__)


@notification_bp.route("/order_chats/", methods=["GET"])
@jwt_required()
@role_required([ADMIN, ASSISTANT, DRIVER])
def list_order_chats():
    identity = get_jwt()
    ctx = ServiceContext(
        query_params=request.args,
        identity=identity,
    )
    outcome = run_service(lambda c: list_order_chats_service(c), ctx)
    response = Response()

    if outcome.error:
        return response.build_unsuccessful_response(outcome.error)

    return response.build_successful_response(
        outcome.data,
        warnings=ctx.warnings,
    )


@notification_bp.route("/order_chats/unseen/", methods=["GET"])
@jwt_required()
@role_required([ADMIN, ASSISTANT, DRIVER])
def list_unseen_order_chats():
    identity = get_jwt()
    ctx = ServiceContext(
        query_params=request.args,
        identity=identity,
    )
    outcome = run_service(lambda c: list_unseen_order_chats_service(c), ctx)
    response = Response()

    if outcome.error:
        return response.build_unsuccessful_response(outcome.error)

    return response.build_successful_response(
        outcome.data,
        warnings=ctx.warnings,
    )


@notification_bp.route("/order_chats/<int:order_chat_id>", methods=["GET"])
@jwt_required()
@role_required([ADMIN, ASSISTANT, DRIVER])
def get_order_chat(order_chat_id: int):
    identity = get_jwt()
    ctx = ServiceContext(
        query_params=request.args,
        identity=identity,
    )
    outcome = run_service(
        lambda c: get_order_chat_service(order_chat_id, c),
        ctx,
    )
    response = Response()

    if outcome.error:
        return response.build_unsuccessful_response(outcome.error)

    return response.build_successful_response(
        outcome.data,
        warnings=ctx.warnings,
    )


@notification_bp.route("/order_chats/", methods=["POST"])
@jwt_required()
@role_required([ADMIN, ASSISTANT, DRIVER])
def create_order_chat():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    ctx = ServiceContext(
        incoming_data=incoming_data,
        identity=identity,
    )
    outcome = run_service(lambda c: create_order_chat_service(c), ctx)
    response = Response()

    if outcome.error:
        return response.build_unsuccessful_response(outcome.error)

    return response.build_successful_response(
        outcome.data,
        warnings=ctx.warnings,
    )


@notification_bp.route("/order_chats/", methods=["PATCH"])
@jwt_required()
@role_required([ADMIN, ASSISTANT, DRIVER])
def update_order_chat():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    ctx = ServiceContext(
        incoming_data=incoming_data,
        identity=identity,
    )
    outcome = run_service(lambda c: update_order_chat_service(c), ctx)
    response = Response()

    if outcome.error:
        return response.build_unsuccessful_response(outcome.error)

    return response.build_successful_response(
        {},
        warnings=ctx.warnings,
    )


@notification_bp.route("/order_chats/", methods=["DELETE"])
@jwt_required()
@role_required([ADMIN, ASSISTANT, DRIVER])
def delete_order_chat():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    ctx = ServiceContext(
        incoming_data=incoming_data,
        identity=identity,
    )
    outcome = run_service(lambda c: delete_order_chat_service(c), ctx)
    response = Response()

    if outcome.error:
        return response.build_unsuccessful_response(outcome.error)

    return response.build_successful_response(
        {},
        warnings=ctx.warnings,
    )


@notification_bp.route("/order_chats/<int:order_chat_id>/read/", methods=["PUT"])
@jwt_required()
@role_required([ADMIN, ASSISTANT, DRIVER])
def create_notification_read( order_chat_id: int ):
    identity = get_jwt()
    ctx = ServiceContext(
        identity=identity,
    )
    outcome = run_service(lambda c: create_notification_read_service(c, order_chat_id), ctx)
    response = Response()

    if outcome.error:
        return response.build_unsuccessful_response(outcome.error)

    return response.build_successful_response(
        outcome.data,
        warnings=ctx.warnings,
    )
