"""
Socket.IO signaling server for real-time features:
- WebRTC signaling between a user's own devices (form handoff)
- WebRTC signaling and telemetry for driver live tracking (per route date)
- Order note push notifications to teammates

All handlers enforce JWT auth (token must include user_id, team_id, role_id).
"""

from functools import wraps
from typing import Dict, Set

from flask import current_app, request
import jwt
from flask_socketio import disconnect, join_room, leave_room

from Delivery_app_BK.socketio_instance import socketio


# Keeps track of which socket session IDs belong to a given user.
active_user_sessions: Dict[int, Set[str]] = {}


def _extract_token() -> str | None:
  """Pull bearer token from query string or Authorization header."""

  auth_header = request.headers.get("Authorization", "")
  
  if auth_header.lower().startswith("bearer "):
    return auth_header.split(" ", 1)[1].strip()

  # Fallback: allow token in query string for browser Socket.IO clients
  query_token = request.args.get("token")

  
  if query_token:
    return query_token.strip()
  
  return None


def _verify_token() -> dict | None:
  """Decode and validate JWT; disconnect on failure."""

  token = _extract_token()


  if not token:
    disconnect()
    return None
  try:
  
    decoded = jwt.decode(
      token,
      current_app.config.get("JWT_SECRET_KEY"),
      algorithms=[current_app.config.get("JWT_ALGORITHM", "HS256")],
    )
  
    return decoded
  except Exception:

    disconnect()
    return None


def authenticated_only(fn):
  """Decorator to ensure socket event handlers have a valid JWT."""

  @wraps(fn)
  def wrapper(*args, **kwargs):

    claims = _verify_token()

    if not claims:
      return None
    return fn(claims, *args, **kwargs)

  return wrapper 


@socketio.on("connect")
@authenticated_only
def handle_connect(claims):

  """On connect, join personal and team rooms for downstream emits."""
  user_id = claims.get("user_id")
  team_id = claims.get("team_id")

  if user_id is None:
    disconnect()
    return

  user_room = f"user:{user_id}"
  team_room = f"team:{team_id}" if team_id is not None else None

  join_room(user_room, sid=request.sid)
  if team_room:
    join_room(team_room, sid=request.sid)

  active_user_sessions.setdefault(user_id, set()).add(request.sid)
  socketio.emit("presence:user_online", {"user_id": user_id}, room=user_room)



@socketio.on("disconnect")
def handle_disconnect():
  """Cleanup user session tracking when a socket disconnects."""
  sid = request.sid
  for user_id, sessions in list(active_user_sessions.items()):
    if sid in sessions:
      sessions.remove(sid)
      if not sessions:
        active_user_sessions.pop(user_id, None)
      break


@socketio.on("webrtc:signal")
@authenticated_only
def handle_webrtc_signal(claims, data):

  """
  Forward WebRTC signaling messages between the same user's devices.
  Expects: { "target_user_id": number, "payload": any }
  If target_user_id is omitted, we assume the sender is targeting their own account.
  """
  user_id = claims.get("user_id")
  target_user_id = data.get("target_user_id") or user_id
  if target_user_id != user_id:
    # Only allow signaling to self-owned devices.
    return
  payload = data.get("payload")
  socketio.emit(
    "webrtc:signal",
    {"from": user_id, "payload": payload},
    room=f"user:{target_user_id}",
    skip_sid=request.sid,  # prevents echoing back to sender
  )


@socketio.on("drivers:subscribe_route")
@authenticated_only
def handle_subscribe_route(claims, data):
  """
  Join a live driver tracking room by date.
  Expects: { "date_key": "YYYY-MM-DD" }
  """
  date_key = (data or {}).get("date_key")
  if not date_key:
    return
  team_id = claims.get("team_id")
  room = f"route-live:{team_id}:{date_key}"
  join_room(room, sid=request.sid)


@socketio.on("drivers:position")
@authenticated_only
def handle_driver_position(claims, data):
  """
  Broadcast a driver's latest position to subscribers of the route date.
  Expects: { "date_key": "YYYY-MM-DD", "driver_id": number, "coords": {lat,lng} }
  """
  date_key = (data or {}).get("date_key")
  team_id = claims.get("team_id")
  if not date_key or team_id is None:
    return
  room = f"route-live:{team_id}:{date_key}"
  socketio.emit(
    "drivers:position",
    {
      "driver_id": data.get("driver_id"),
      "coords": data.get("coords"),
      "timestamp": data.get("timestamp"),
    },
    room=room,
  )


@socketio.on("orders:note")
@authenticated_only
def handle_order_note(claims, data):
  """
  Push order note updates to everyone in the same team.
  Expects: { "order_id": number, "note": string }
  """
  team_id = claims.get("team_id")
  if team_id is None:
    return
  socketio.emit(
    "orders:note",
    {"order_id": data.get("order_id"), "note": data.get("note"), "author_id": claims.get("user_id")},
    room=f"team:{team_id}",
  )


@socketio.on("external_form:join_user")
@authenticated_only
def handle_external_form_join_user(claims, data):

    team_id = claims.get("team_id")
    target_user_id = (data or {}).get("user_id")
    
    if team_id is None or target_user_id is None:
        return

    room = f"external_form:{team_id}:{target_user_id}"
    
    join_room(room, sid=request.sid)

  
@socketio.on("external_form:leave_user")
@authenticated_only
def handle_external_form_leave_user(claims, data):

    team_id = claims.get("team_id")
    target_user_id = (data or {}).get("user_id")

    if team_id is None or target_user_id is None:
        return

    room = f"external_form:{team_id}:{target_user_id}"
    leave_room(room, sid=request.sid)


@socketio.on("external_form:submit_user")
@authenticated_only
def handle_external_form_submit_user(claims, data):

    team_id = claims.get("team_id")
    target_user_id = (data or {}).get("user_id")
    form_data = (data or {}).get("form_data")
    
    if team_id is None or target_user_id is None or not form_data:
        return

    room = f"external_form:{team_id}:{target_user_id}"

    socketio.emit(
        "external_form:received",
        {
            "form_data": form_data,
            "submitted_by": claims.get("user_id"),
        },
        room=room,
        skip_sid=request.sid
    )


@socketio.on("external_form:request_user")
@authenticated_only
def handle_external_form_request_user(claims, data):

    team_id = claims.get("team_id")
    target_user_id = (data or {}).get("user_id")
    request_data = (data or {}).get("request_data")

    if team_id is None or target_user_id is None:
        return

    room = f"external_form:{team_id}:{target_user_id}"

    socketio.emit(
        "external_form:requested",
        {
            "request_data": request_data or {},
            "requested_by": claims.get("user_id"),
        },
        room=room,
        skip_sid=request.sid
    )
