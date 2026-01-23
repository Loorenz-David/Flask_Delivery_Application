import os
from flask import Blueprint, request

from Delivery_app_BK.errors import ValidationFailed
from Delivery_app_BK.routers.http.response import Response
from Delivery_app_BK.services.context import ServiceContext
from Delivery_app_BK.services.run_service import run_service
from Delivery_app_BK.services.commands.seed import seed_initial_data as seed_initial_data_service


seed_bp = Blueprint("api_v2_seed_bp", __name__)


def _is_valid(key) -> bool:
    secrete_key = os.environ.get("SECRET_KEY")
    
    if not secrete_key:
        return False
    
    return  secrete_key == key


SECRETE_KEY = os.environ.get("SECRET_KEY")

@seed_bp.route("/", methods=["POST"])
def seed():
    response = Response()
    data = request.get_json(silent=True)
    key = data.get("key")

    if not key:
        return response.build_unsuccessful_response(
            ValidationFailed("Missing key")
        )
    
    if not _is_valid(key):
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
