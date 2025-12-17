import os

from flask import Blueprint
from sqlalchemy import or_

from Delivery_app_BK.models import db
from Delivery_app_BK.models.tables.users_models import UserRole
from Delivery_app_BK.routers.utils.response import Response
from .seed_roles_data import DEFAULT_ROLES

seed_roles_bp = Blueprint("seed_roles_bp", __name__)


def _is_development() -> bool:
    env_value = os.environ.get("FLASK_ENVIROMENT", "") or os.environ.get("FLASK_ENV", "")
    return env_value.lower() == "development"


@seed_roles_bp.route("/roles", methods=["POST"])
def seed_roles():
    response = Response()

    if not _is_development():
        response.set_error("Seeding is only allowed if active seed is enabled.", 403)
        return response.build()

    try:
        created, updated = [], []
        for role_entry in DEFAULT_ROLES:
            role_id = role_entry["id"]
            role_name = role_entry["role"]
            description = role_entry.get("description")

            existing = (
                UserRole.query.filter(
                    or_(
                        UserRole.id == role_id,
                        UserRole.role == role_name,
                    )
                )
                .order_by(UserRole.id.asc())
                .first()
            )

            if not existing:
                new_role = UserRole(id=role_id, role=role_name, description=description)
                db.session.add(new_role)
                created.append(role_name)
                continue

            has_changes = False
            if existing.role != role_name:
                existing.role = role_name
                has_changes = True
            if description is not None and existing.description != description:
                existing.description = description
                has_changes = True
            if has_changes:
                updated.append(role_name)

        db.session.commit()
        response.set_message("Seeding completed.")
        response.set_payload(
            {
                "created": created,
                "updated": updated,
                "total_seeded": len(created) + len(updated),
            }
        )
        return response.build()
    except Exception as e:
        db.session.rollback()
        response.set_error(f"Failed to seed roles: {str(e)}", 500)
        return response.build()
