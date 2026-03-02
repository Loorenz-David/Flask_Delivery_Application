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
from Delivery_app_BK.services.commands.plan.local_delivery.route_solution.stops.update_route_stop_position import (
    update_route_stop_position as update_route_stop_position_service,
)


from Delivery_app_BK.services.commands.plan.local_delivery.route_solution.select_route_solution import (
    select_route_solution as select_route_solution_service,
)
from Delivery_app_BK.services.queries.route_solutions.get_route_solution import (
    get_route_solution as get_route_solution_service,
)
from Delivery_app_BK.route_optimization.orchestrator import (
    optimize_local_delivery_plan,
)


route_solution_bp = Blueprint("api_v2_route_solution_bp", __name__)


@route_solution_bp.route(
    "/stops/<int:route_stop_id>/position/<int:position>",
    methods=["PATCH"],
)
@jwt_required()
@role_required([ADMIN, ASSISTANT, DRIVER])
def update_route_stop_position(
    route_stop_id: int,
    position: int,
):
    identity = get_jwt()
    ctx = ServiceContext(identity=identity)
    
    outcome = run_service(
        lambda c: update_route_stop_position_service(
            c,
            route_stop_id,
            position,
        ),
        ctx,
    )
    response = Response()

    if outcome.error:
        return response.build_unsuccessful_response(outcome.error)

    return response.build_successful_response(
        outcome.data or {},
        warnings=ctx.warnings,
    )







@route_solution_bp.route("/<int:route_solution_id>/select", methods=["PATCH"])
@jwt_required()
@role_required([ADMIN, ASSISTANT, DRIVER])
def select_route_solution(route_solution_id: int):
    identity = get_jwt()
    ctx = ServiceContext(identity=identity)
    outcome = run_service(
        lambda c: select_route_solution_service(c, route_solution_id),
        ctx,
    )
    response = Response()

    if outcome.error:
        return response.build_unsuccessful_response(outcome.error)

    return response.build_successful_response(
        outcome.data or {},
        warnings=ctx.warnings,
    )


@route_solution_bp.route("/<int:route_solution_id>", methods=["GET"])
@jwt_required()
@role_required([ADMIN, ASSISTANT, DRIVER])
def get_route_solution(route_solution_id: int):
    identity = get_jwt()
    return_stops = request.args.get("return_stops", "false").lower() == "true"
    ctx = ServiceContext(identity=identity)
    outcome = run_service(
        lambda c: get_route_solution_service(route_solution_id, c, return_stops),
        ctx,
    )
    response = Response()

    if outcome.error:
        return response.build_unsuccessful_response(outcome.error)

    return response.build_successful_response(
        outcome.data or {},
        warnings=ctx.warnings,
    )


@route_solution_bp.route("/optimize", methods=["POST"])
@jwt_required()
@role_required([ADMIN, ASSISTANT, DRIVER])
def create_route_optimization():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True) or {}
    ctx = ServiceContext(
        incoming_data=incoming_data,
        identity=identity,
    )

    outcome = optimize_local_delivery_plan(ctx)
    response = Response()

    if outcome.error:
        return response.build_unsuccessful_response(outcome.error)

    return response.build_successful_response(
        outcome.data or {},
        warnings=ctx.warnings,
    )


@route_solution_bp.route("/optimize", methods=["PATCH"])
@jwt_required()
@role_required([ADMIN, ASSISTANT, DRIVER])
def update_route_optimization():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True) or {}
    ctx = ServiceContext(
        incoming_data=incoming_data,
        identity=identity,
    )
    response = Response()
   
    
    outcome = optimize_local_delivery_plan(ctx)

    if outcome.error:
        return response.build_unsuccessful_response(outcome.error)

    return response.build_successful_response(
        outcome.data or {},
        warnings=ctx.warnings,
    )
