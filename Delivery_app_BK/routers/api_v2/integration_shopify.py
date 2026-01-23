
from flask import Blueprint, request, redirect, render_template
from flask_jwt_extended import jwt_required, get_jwt


from Delivery_app_BK.services.context import ServiceContext
from Delivery_app_BK.services.run_service import run_service

from Delivery_app_BK.services.commands.integration_shopify.auth import connect_to_shopify_store, handle_shopify_oauth_callback

from ..http.response import Response

shopify_bp = Blueprint("api_v2_integration_shopify", __name__)




@shopify_bp.route("/connect", methods=["GET"])
@jwt_required()
def connect_shopify():
    identity = get_jwt()
    shop = request.args.get("shop")  # my-store.myshopify.com
    ctx = ServiceContext(
        identity = identity
    )

    outcome = run_service( lambda c: connect_to_shopify_store( c, shop), ctx)

    response = Response()

    if outcome.error:
        return response.build_unsuccessful_response(outcome.error)

    return response.build_successful_response(
        outcome.data,
        warnings=ctx.warnings,
    )
   
# OAuth callback is unauthenticated; user binding is resolved via OAuth state
@shopify_bp.route("/oauth/callback", methods=["GET"])
def shopify_oauth_callback():
    ctx = ServiceContext()

    outcome = run_service(
        lambda c: handle_shopify_oauth_callback(c, request.args.to_dict()),
        ctx
    )

    if outcome.error:
        return "Shopify OAuth failed", 400

    return redirect(outcome.data["redirect_url"])


@shopify_bp.route("/app")
def shopify_app_home():
    shop = request.args.get("shop")
    return render_template("shopify_app.html", shop=shop)