# Third-party dependencies
from flask import request

# Locat Imports
from . import route_bp
from Delivery_app_BK.routers.utils.response import Response
from Delivery_app_BK.models import Route
from Delivery_app_BK.models.managers import FindObjects

@route_bp.route("/query_route",methods=['POST'])
def query_route ():
    response = Response()
    incoming_data = request.get_json()

    FindObjects.find_objects(
        response=response,
        Model=Route,
        incoming_data=incoming_data
    )
    
    return response.build()
