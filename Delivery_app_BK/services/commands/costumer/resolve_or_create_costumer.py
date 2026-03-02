from __future__ import annotations

from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import selectinload

from Delivery_app_BK.models import Costumer, CostumerAddress, CostumerPhone, db
from Delivery_app_BK.services.utils import require_team_id

from ...context import ServiceContext
from ...requests.costumer.common import (
    normalize_email,
    normalized_phone_string,
    validate_and_normalize_phone,
)
from ..utils.client_id_generator import generate_client_id


def resolve_or_create_costumer(
    ctx: ServiceContext,
    first_name: str | None,
    last_name: str | None,
    email: str | None,
    primary_phone: dict[str, Any] | None,
    address: dict[str, Any] | None,
) -> Costumer:
    team_id = require_team_id(ctx)
    normalized_email = normalize_email(email)
    normalized_phone = validate_and_normalize_phone(primary_phone)

    if normalized_email:
        existing_by_email = (
            db.session.query(Costumer)
            .filter(
                Costumer.team_id == team_id,
                func.lower(Costumer.email) == normalized_email,
            )
            .first()
        )
        if existing_by_email:
            return existing_by_email

    if normalized_phone:
        by_phone = _find_by_normalized_phone(team_id, normalized_phone_string(normalized_phone))
        if by_phone:
            return by_phone

    created = Costumer(
        team_id=team_id,
        client_id=generate_client_id("costumer"),
        first_name=first_name or "",
        last_name=last_name or "",
        email=normalized_email,
    )
    db.session.add(created)
    db.session.flush()

    if address is not None:
        address_row = CostumerAddress(
            team_id=team_id,
            costumer_id=created.id,
            client_id=generate_client_id("costumer_address"),
            label=address.get("label") if isinstance(address, dict) else None,
            address=address if isinstance(address, dict) else None,
        )
        db.session.add(address_row)
        db.session.flush()
        created.default_address_id = address_row.id

    if normalized_phone is not None:
        phone_row = CostumerPhone(
            team_id=team_id,
            costumer_id=created.id,
            client_id=generate_client_id("costumer_phone"),
            phone=normalized_phone,
        )
        db.session.add(phone_row)
        db.session.flush()
        created.default_primary_phone_id = phone_row.id

    return created


def _find_by_normalized_phone(team_id: int, expected: str | None) -> Costumer | None:
    if not expected:
        return None

    candidates = (
        db.session.query(Costumer)
        .options(selectinload(Costumer.phones))
        .filter(Costumer.team_id == team_id)
        .all()
    )

    for costumer in candidates:
        for phone in costumer.phones or []:
            phone_payload = getattr(phone, "phone", None) or {}
            prefix = str(phone_payload.get("prefix") or "").strip().replace(" ", "")
            number = str(phone_payload.get("number") or "").strip().replace(" ", "")
            if prefix and number and f"{prefix}{number}" == expected:
                return costumer

    return None
