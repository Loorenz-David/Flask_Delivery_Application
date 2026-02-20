from __future__ import annotations

import os
from typing import Any, Dict

from google.maps import routeoptimization_v1
from google.protobuf.json_format import MessageToDict

from Delivery_app_BK.errors import ValidationFailed
from Delivery_app_BK.route_optimization.domain.models import (
    OptimizationRequest,
    OptimizationResult,
)
from Delivery_app_BK.route_optimization.providers.base import RouteOptimizationProvider
from Delivery_app_BK.route_optimization.providers.google.mapper import (
    GoogleRequestMapper,
    GoogleResponseMapper,
)


class GoogleRouteOptimizationProvider(RouteOptimizationProvider):
    name = "google_route_optimization"

    def __init__(self, project_id: str | None = None, location: str | None = None) -> None:
        project_id = project_id or os.environ.get("GOOGLE_ROUTE_OPTIMIZATION_PROJECT_ID")
        location = location or os.environ.get("GOOGLE_ROUTE_OPTIMIZATION_LOCATION", "us-central1")
        if not project_id:
            raise ValidationFailed("GOOGLE_ROUTE_OPTIMIZATION_PROJECT_ID is not configured.")

        self.parent = f"projects/{project_id}"
        self.location = location
        self.client = routeoptimization_v1.RouteOptimizationClient()

    def optimize(self, request: OptimizationRequest) -> OptimizationResult:
        payload = GoogleRequestMapper.build_request(self.parent, request)
       
        # raise Exception('manual raise')
        response = self.client.optimize_tours(request=payload)
        message = getattr(response, "_pb", response)
        response_dict = MessageToDict(message, preserving_proto_field_name=True)
        return GoogleResponseMapper.parse_response(response_dict, request)
