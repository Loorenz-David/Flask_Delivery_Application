

# Third-part dependencies
from flask import Blueprint, request
from marshmallow import ValidationError
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity


# Local application imports 
from Delivery_app_BK.models import User
from Delivery_app_BK.models.schemas.users_schema import UserSchema
from Delivery_app_BK.routers.utils.response import Response


# Creates Blueprint
# All routers that need access protection are wrap with @jwt_required()
token_generation_bp = Blueprint("token_generation_bp",__name__)


# logs user in by returning a access and refresh token
@token_generation_bp.route('/login',methods=['POST','GET'])
def login():
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data)
    if response.error:
        return response.build()

    incoming_data = response.incoming_data or {}

    # Validates incoming data
    try:
        valid_data = UserSchema().load(incoming_data)
        email = valid_data["email"]
        password = valid_data["password"]

    except ValidationError as err:
        response.set_error(
            message=err.messages,
            status=400
        )
        response.set_message("Validation failed")

        return response.build()

    # Query for user base on email and return access token if valid password match
    try:
        # query for user and pasword match check
        query = User.query
        user:User = query.filter(User.email == email).first()
        if not user:
            raise Exception("Incorrect loging information")
        
        if not user.get_password() == password:
            raise Exception("Incorrect loging information")
        
        # generates access token ( default: expires in 1 hour ). 
        # generates refresh token ( default: expires in 7 days ). 
        # to change this default behaviors modify Delivery_app_BK __init__.py, keys with substrings JWT and EXPIRES
        identity_data = {"user_id": user.id, "team_id": user.team_id}
        access_token = create_access_token(identity=identity_data)
        refresh_token = create_refresh_token(identity=identity_data)

        # set the return payload 
        response.set_payload({
            "access_token":access_token,
            "refresh_token":refresh_token,
            "user":{"id":user.id,"email":user.email}
        })

        # return status 200 with payload
        return response.build()

    # error on query
    except Exception as e:
        response.set_message(message=str(e))
        response.set_error(message=str(e))

        return response.build()
    

# generates a new access token if refresh token is valid
@token_generation_bp.route("/refresh_token",methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    response = Response()

    # gets the user id coming from the refresh token,
    # and generates a new access token
    identity_data = get_jwt_identity()
    new_access = create_access_token(identity=identity_data)

    # sets the payload for the response
    response.set_payload({
        'access_token':new_access
    })

    # return status 200 with payload
    return response.build()
