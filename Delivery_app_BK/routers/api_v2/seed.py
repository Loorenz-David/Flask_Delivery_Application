import os
from flask import Blueprint, request

from Delivery_app_BK.errors import ValidationFailed
from Delivery_app_BK.routers.http.response import Response
from Delivery_app_BK.services.context import ServiceContext
from Delivery_app_BK.services.run_service import run_service
from Delivery_app_BK.services.commands.seed import seed_initial_data as seed_initial_data_service


seed_bp = Blueprint("api_v2_seed_bp", __name__)


def _is_development() -> bool:
    return os.environ.get("FLASK_ENV", "development") == "development"


@seed_bp.route("/", methods=["POST"])
def seed():
    response = Response()
    if not _is_development():
        return response.build_unsuccessful_response(
            ValidationFailed("Seed endpoint available only in development.")
        )

    incoming_data = request.get_json(silent=True)
    ctx = ServiceContext(
        incoming_data=incoming_data,
        inject_team_id=False,
        check_team_id=False,
        skip_id_instance_injection=False,
    )

    outcome = run_service(lambda c: seed_initial_data_service(c), ctx)

    if outcome.error:
        return response.build_unsuccessful_response(outcome.error)

    return response.build_successful_response(
        {},
        warnings=ctx.warnings,
    )
