from flask_jwt_extended import jwt_required, get_jwt
from Delivery_app_BK.routers.utils.role_decorator import role_required

from . import route_bp
from Delivery_app_BK.routers.utils.response import Response
from Delivery_app_BK.models import User, RouteState, ItemState, ItemPosition, UserWarehouse
from Delivery_app_BK.models.managers.object_searcher import FindObjects

ROUTE_STATE_FIELDS = ['id', 'name']
DRIVER_FIELDS = ['id', 'username', 'profile_picture']
ITEM_STATE_FIELDS = ['id', 'name', 'color', 'default', 'description','priority']
ITEM_POSITION_FIELDS = ['id', 'name', 'default', 'description']
WAREHOUSE_FIELDS = ['id', 'name', 'location']


def _create_incoming_payload(requested_fields: list) -> dict:
  return {
    'data': {
      'requested_data': requested_fields,
    },
    'is_compress': False,
  }


def _collect_dataset(Model, requested_fields, identity):
  response = Response(incoming_data=_create_incoming_payload(requested_fields), identity=identity)
  success = FindObjects.find_objects(
    response=response,
    Model=Model,
    identity=identity,
    compress_data=False,
  )

  if response.status >= 400:
    message = response.error or f'Failed to fetch data for {Model.__name__}'
    raise ValueError(message)

  payload = response.payload or {}
  items = payload.get('items', [])
  return items if success or response.status < 400 else []


def _normalize_drivers(drivers):
  normalized = []
  for driver in drivers:
    normalized.append({
      'id': driver.get('id'),
      'username': driver.get('username'),
      'profile_picture': driver.get('profile_picture'),
      'phone_number': driver.get('phone_number'),
    })
  return normalized


def _normalize_route_states(states):
  normalized = []
  for state in states:
    normalized.append({
      'id': state.get('id'),
      'name': state.get('name'),
      'color': state.get('color'),
      'default': state.get('default'),
    })
  return normalized


@route_bp.route('/main_dependencies', methods=['GET'])
@jwt_required()
@role_required([1, 2, 3])
def query_route_main_dependencies():
  identity = get_jwt()
  response = Response(identity=identity)

  try:
    route_states = _collect_dataset(RouteState, ROUTE_STATE_FIELDS, identity)
    drivers = _collect_dataset(User, DRIVER_FIELDS, identity)
    item_states = _collect_dataset(ItemState, ITEM_STATE_FIELDS, identity)
    item_positions = _collect_dataset(ItemPosition, ITEM_POSITION_FIELDS, identity)
    default_warehouses = _collect_dataset(UserWarehouse, WAREHOUSE_FIELDS, identity)

    payload = {
      'route_states': _normalize_route_states(route_states),
      'drivers': _normalize_drivers(drivers),
      'item_states': item_states,
      'item_positions': item_positions,
      'default_warehouses': default_warehouses,
    }

    response.set_payload(payload)
    response.compress_payload()
    response.set_message('Dependencies fetched successfully.')
  except ValueError as error:
    response.set_message('Failed to fetch main dependencies.')
    response.set_error(str(error), status=400)

  return response.build()
