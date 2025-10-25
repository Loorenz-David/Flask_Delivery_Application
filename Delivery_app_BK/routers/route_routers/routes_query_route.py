# Third-party dependencies
from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required

# Locat Imports
from . import route_bp
from Delivery_app_BK.routers.utils.response import Response
from Delivery_app_BK.models import Route
from Delivery_app_BK.models.managers.object_searcher import FindObjects

@route_bp.route("/query_route",methods=['POST'])
@jwt_required()
def query_route ():
    identity = get_jwt_identity()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    FindObjects.find_objects(
        response=response,
        Model=Route,
        identity=identity,
    )
    
    return response.build()
