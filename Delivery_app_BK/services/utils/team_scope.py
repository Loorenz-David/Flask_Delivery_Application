from __future__ import annotations

from typing import Any, Dict, Optional


def get_team_id(identity: Optional[Dict[str, Any]]) -> Optional[int]:
    if isinstance(identity, dict):
        return identity.get("team_id")
    return None


def require_team_id(identity: Optional[Dict[str, Any]]) -> int:
    team_id = get_team_id(identity)
    if team_id is None:
        raise PermissionError("User is not assigned to a team")
    return team_id


def ensure_instance_in_team(instance: Any, identity: Optional[Dict[str, Any]]) -> None:
    if not hasattr(instance, "team_id"):
        return
    team_id = require_team_id(identity)
    if instance.team_id != team_id:
        raise PermissionError("You are not authorized to access this resource")


def model_requires_team(Model: Any) -> bool:
    return hasattr(Model, "team_id")


def inject_team_id(fields: Dict[str, Any], identity: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not isinstance(fields, dict):
        raise ValueError("Fields must be provided as a dictionary")

    updated_fields = dict(fields)
    if "team_id" not in updated_fields:
        updated_fields["team_id"] = require_team_id(identity)
    return updated_fields
