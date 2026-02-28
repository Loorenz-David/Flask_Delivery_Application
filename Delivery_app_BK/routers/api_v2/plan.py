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
from Delivery_app_BK.services.domain.plan.plan_states import PlanStateId
from Delivery_app_BK.services.queries.plan.list_delivery_plans import (
    list_delivery_plans as list_delivery_plans_service,
)
from Delivery_app_BK.services.queries.plan.get_plan import (
    get_plan as get_plan_service,
)
from Delivery_app_BK.services.commands.plan.create_plan import (
    create_plan as create_plan_service,
)
from Delivery_app_BK.services.commands.plan.update_plan import (
    update_plan as update_plan_service,
)

from Delivery_app_BK.services.commands.plan.local_delivery.update_settings import (
    update_local_delivery_settings as update_local_delivery_plan_settings_service
)
from Delivery_app_BK.services.commands.plan.delete_plan import (
    delete_plan as delete_plan_service,
)
from Delivery_app_BK.services.commands.plan.mark_plan_state import (
    mark_plan_state as mark_plan_state_service
)
from Delivery_app_BK.services.commands.plan.plan_states.update_plan_state import (
    update_plan_state as update_plan_state_service,
)
from Delivery_app_BK.services.queries.order.list_orders import (
    list_orders as list_orders_service,
)
from Delivery_app_BK.services.queries.plan_types.get_plan_type import (
    get_plan_type as get_plan_type_service,
)
from Delivery_app_BK.services.queries.plan_states.list_plan_states import (
    list_plan_states as list_plan_states_service,
)


plan_bp = Blueprint("api_v2_plan_bp", __name__)


@plan_bp.route("/", methods=["GET"])
@jwt_required()
@role_required([ADMIN, ASSISTANT, DRIVER])
def list_delivery_plans():
    identity = get_jwt()
    ctx = ServiceContext(
        query_params=request.args,
        identity=identity,
    )

    outcome = run_service(lambda c: list_delivery_plans_service(c), ctx)
    response = Response()

    if outcome.error:
        return response.build_unsuccessful_response(outcome.error)

    return response.build_successful_response(
        outcome.data,
        warnings=ctx.warnings,
    )


@plan_bp.route("/states/", methods=["GET"])
@jwt_required()
@role_required([ADMIN, ASSISTANT, DRIVER])
def list_plan_states():
    identity = get_jwt()
    ctx = ServiceContext(
        query_params=request.args,
        identity=identity,
        inject_team_id = False,
    )
    outcome = run_service(lambda c: list_plan_states_service(c), ctx)
    response = Response()

    if outcome.error:
        return response.build_unsuccessful_response(outcome.error)

    return response.build_successful_response(
        outcome.data,
        warnings=ctx.warnings,
    )


@plan_bp.route("/", methods=["POST"])
@jwt_required()
@role_required([ADMIN, ASSISTANT, DRIVER])
def create_plan():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True) or {}
    ctx = ServiceContext(
        incoming_data=incoming_data,
        identity=identity,
    )
    outcome = run_service(lambda c: create_plan_service(c), ctx)
    response = Response()

    if outcome.error:
        return response.build_unsuccessful_response(outcome.error)

    return response.build_successful_response(
        outcome.data,
        warnings=ctx.warnings,
    )


@plan_bp.route("/", methods=["PATCH"])
@jwt_required()
@role_required([ADMIN, ASSISTANT, DRIVER])
def update_plan():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True) or {}
    prevent_event_bus = incoming_data.pop("prevent_event_bus", False)
    ctx = ServiceContext(
        incoming_data=incoming_data,
        identity=identity,
        prevent_event_bus = prevent_event_bus
    )
    outcome = run_service(lambda c: update_plan_service(c), ctx)
    response = Response()

    if outcome.error:
        return response.build_unsuccessful_response(outcome.error)

    return response.build_successful_response(
        {},
        warnings=ctx.warnings,
    )


@plan_bp.route("/local_delivery", methods=["PATCH"])
@jwt_required()
@role_required([ADMIN, ASSISTANT, DRIVER])
def update_local_delivery_plan_settings():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True) or {}
    prevent_event_bus = incoming_data.pop("prevent_event_bus", False)
    ctx = ServiceContext(
        incoming_data=incoming_data,
        identity=identity,
        prevent_event_bus = prevent_event_bus
    )
    outcome = run_service(
        lambda c: update_local_delivery_plan_settings_service(c),
        ctx,
    )
    response = Response()

    if outcome.error:
        return response.build_unsuccessful_response(outcome.error)
   
    return response.build_successful_response(
        outcome.data,
        warnings=ctx.warnings,
    )


@plan_bp.route("/", methods=["DELETE"])
@jwt_required()
@role_required([ADMIN, ASSISTANT, DRIVER])
def delete_plan():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True) or {}
    ctx = ServiceContext(
        incoming_data=incoming_data,
        identity=identity,
    )
    outcome = run_service(lambda c: delete_plan_service(c), ctx)
    response = Response()

    if outcome.error:
        return response.build_unsuccessful_response(outcome.error)

    return response.build_successful_response(
        {},
        warnings=ctx.warnings,
    )


@plan_bp.route("/<int:plan_id>", methods=["GET"])
@jwt_required()
@role_required([ADMIN, ASSISTANT, DRIVER])
def get_plan(plan_id: int):
    identity = get_jwt()
    ctx = ServiceContext(
        query_params=request.args,
        identity=identity,
    )
    outcome = run_service(lambda c: get_plan_service(plan_id, c), ctx)
    response = Response()

    if outcome.error:
        return response.build_unsuccessful_response(outcome.error)

    return response.build_successful_response(
        outcome.data,
        warnings=ctx.warnings,
    )


@plan_bp.route("/<int:plan_id>/type/<string:plan_type>", methods=["GET"])
@jwt_required()
@role_required([ADMIN, ASSISTANT, DRIVER])
def get_plan_type(plan_id: int, plan_type: str):
    identity = get_jwt()
    ctx = ServiceContext(
        query_params=request.args,
        identity=identity,
    )
    outcome = run_service(
        lambda c: get_plan_type_service(plan_id, plan_type, c),
        ctx,
    )
    response = Response()

    if outcome.error:
        return response.build_unsuccessful_response(outcome.error)

    return response.build_successful_response(
        outcome.data,
        warnings=ctx.warnings,
    )


@plan_bp.route("/<int:plan_id>/orders/", methods=["GET"])
@jwt_required()
@role_required([ADMIN, ASSISTANT, DRIVER])
def list_plan_orders(plan_id: int):

    identity = get_jwt()
    ctx = ServiceContext(
        query_params=request.args,
        identity=identity,
    )
    outcome = run_service(lambda c: list_orders_service(c, plan_id=plan_id), ctx)
    response = Response()

    if outcome.error:
        return response.build_unsuccessful_response(outcome.error)

    return response.build_successful_response(
        outcome.data,
        warnings=ctx.warnings,
    )


@plan_bp.route("/<int:plan_id>/state/<int:state_id>", methods=["PATCH"])
@jwt_required()
@role_required([ADMIN, ASSISTANT, DRIVER])
def update_plan_state(plan_id: int, state_id: int):
    identity = get_jwt()
    incoming_data = request.get_json(silent=True) or {}
    prevent_event_bus = incoming_data.pop("prevent_event_bus", False)
    ctx = ServiceContext(
        identity=identity,
        prevent_event_bus=prevent_event_bus

    )
    outcome = run_service(
        lambda c: update_plan_state_service(c, plan_id, state_id),
        ctx,
    )
    response = Response()

    if outcome.error:
        return response.build_unsuccessful_response(outcome.error)

    return response.build_successful_response(
        {},
        warnings=ctx.warnings,
    )


@plan_bp.route("/<int:delivery_plan_id>/plan-is-ready", methods=["PATCH"])
@jwt_required()
@role_required([ADMIN, ASSISTANT, DRIVER])
def mark_plan_state(delivery_plan_id: int):
    identity = get_jwt()
    ctx = ServiceContext(
        identity=identity,
    )

    outcome = run_service(
        lambda c: mark_plan_state_service(c,delivery_plan_id, PlanStateId.READY),
        ctx,
    )
    response = Response()

    if outcome.error:
        return response.build_unsuccessful_response(outcome.error)

    return response.build_successful_response(
        outcome.data or {},
        warnings=ctx.warnings,
    )
