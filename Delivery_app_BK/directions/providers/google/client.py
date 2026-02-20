from __future__ import annotations

import os
from typing import Any, Dict

from Delivery_app_BK.errors import ValidationFailed
from Delivery_app_BK.directions.domain.models import DirectionsRequest, DirectionsResult
from Delivery_app_BK.directions.providers.base import DirectionsProvider
from Delivery_app_BK.directions.providers.google.mapper import (
    GoogleDirectionsRequestMapper,
    GoogleDirectionsResponseMapper,
)


class GoogleDirectionsProvider(DirectionsProvider):
    name = "google_compute_routes"

    def __init__(self, project_id: str | None = None) -> None:
        project_id = project_id or os.environ.get("GOOGLE_ROUTE_OPTIMIZATION_PROJECT_ID")
        if not project_id:
            raise ValidationFailed("GOOGLE_ROUTE_OPTIMIZATION_PROJECT_ID is not configured.")
        self.project_id = project_id

    def compute(self, request: DirectionsRequest) -> DirectionsResult:
        try:
            from google.maps import routing_v2
        except Exception as exc:  # pragma: no cover - runtime dependency
            raise ValidationFailed("google.maps.routing_v2 is not available.") from exc

        client = routing_v2.RoutesClient()
        payload, field_mask = GoogleDirectionsRequestMapper.build_request(request)
      
        
        response = client.compute_routes(
            request=payload,
            metadata=[("x-goog-fieldmask", field_mask)],
        )
     

        return GoogleDirectionsResponseMapper.parse_response(response, request)
