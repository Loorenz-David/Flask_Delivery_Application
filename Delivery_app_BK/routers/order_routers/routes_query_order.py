# Third-party dependencies
from flask import request

# Locat Imports
from . import order_bp
from Delivery_app_BK.routers.utils.response import Response
from Delivery_app_BK.models import Order
from Delivery_app_BK.models.managers import FindObjects

@order_bp.route("/query_order",methods=['POST'])
def query_order ():
    response = Response()
    incoming_data = request.get_json()

    FindObjects.find_objects(
        response=response,
        Model=Order,
        incoming_data=incoming_data
    )
    
    return response.build()
