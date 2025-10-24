# Third-party dependencies
from flask import request

# Locat Imports
from . import order_bp
from Delivery_app_BK.routers.utils.response import Response
from Delivery_app_BK.models import Order
from Delivery_app_BK.models.managers.object_searcher import FindObjects

@order_bp.route("/query_order",methods=['POST'])
def query_order ():
    print('at the beginning ')
    response = Response()
    incoming_data = request.get_json()
    print('incoming data: ', incoming_data)
    FindObjects.find_objects(
        response=response,
        Model=Order,
        incoming_data=incoming_data
    )
    print("RESPONSE OBJ")
    print(response)
    return response.build()
