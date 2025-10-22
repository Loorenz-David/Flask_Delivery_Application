# Third-party dependencies
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity

# Locat Imports
from . import item_bp
from Delivery_app_BK.routers.utils.response import Response
from Delivery_app_BK.models import Item, db
from Delivery_app_BK.models.managers.object_searcher import ObjectSearcher

@item_bp.route("/query_item",methods=['POST'])
def query_item ():
    response = Response()
    incoming_data = request.get_json()

    # create an instance of ObjectSearcher
    searcher = ObjectSearcher(Obj=Item, data=incoming_data, response=response)

    # perform the query using build_query method
    searcher.build_query()

    # if item_query is false
    if not searcher.found_objects:
        return response.build()
    
    # unpacks the found object into a dictionary format
    searcher.unpack()

    # add the unpacked data to the response
    response.set_payload(searcher.unpacked_data)

    # compresses the payload to gzip
    response.compress_payload()
    
    return response.build()