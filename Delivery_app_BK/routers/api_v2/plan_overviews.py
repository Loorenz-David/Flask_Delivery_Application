from flask import Blueprint
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
from Delivery_app_BK.services.overviews.local_delivery_overview import (
    local_delivery_overview as local_delivery_overview_service,
)


plan_overviews_bp = Blueprint("api_v2_plan_overviews_bp", __name__)


@plan_overviews_bp.route("/<int:plan_id>/local_delivery/", methods=["GET"])
@jwt_required()
@role_required([ADMIN, ASSISTANT, DRIVER])
def get_local_delivery_overview(plan_id: int):
    identity = get_jwt()
    ctx = ServiceContext(identity=identity)
    outcome = run_service(
        lambda c: local_delivery_overview_service(c, plan_id),
        ctx,
    )
    response = Response()

    if outcome.error:
        return response.build_unsuccessful_response(outcome.error)

    return response.build_successful_response(
        outcome.data,
        warnings=ctx.warnings,
    )
