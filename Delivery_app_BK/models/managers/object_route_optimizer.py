import json
import os
from datetime import datetime, time as time_cls, timezone
from typing import Any, Dict, List, Optional, TYPE_CHECKING
import pprint

from google.api_core.client_options import ClientOptions
from google.maps import routeoptimization_v1
from google.oauth2 import service_account
from google.protobuf.json_format import MessageToDict

from Delivery_app_BK.models import db, Route, Order
from Delivery_app_BK.models.managers.object_searcher import GetObject
from Delivery_app_BK.models import UserVehicle  # type: ignore


if TYPE_CHECKING:
    from Delivery_app_BK.routers.utils.response import Response

DEFAULT_ROUTE_MODIFIERS = {
    "avoid_tolls": False,
    "avoid_highways": False,
    "avoid_ferries": False,
    "avoid_indoor": False,
}

DEFAULT_VEHICLE_VALUES = {
    "cost_per_kilometer": 1.0,
    "travel_mode": "DRIVING",
}

DEFAULT_OBJECTIVES = [
    {"type":{"MIN_TRAVEL_TIME": True}},
]

class GoogleRouteOptimizationClient:
    """
    Thin wrapper around the Google Maps Route Optimization client that
    centralizes configuration and keeps request creation tidy.
    """

    def __init__(
        self,
        project_id: Optional[str] = None,
        location: Optional[str] = None,
    ) -> None:

        project_id = project_id or os.environ.get("GOOGLE_ROUTE_OPTIMIZATION_PROJECT_ID")
        location = location or os.environ.get("GOOGLE_ROUTE_OPTIMIZATION_LOCATION", "us-central1")

        if not project_id:
            raise EnvironmentError("GOOGLE_ROUTE_OPTIMIZATION_PROJECT_ID is not configured.")

        self.parent = f"projects/{project_id}"

        if os.environ.get("FLASK_ENVIROMENT") == "development":
            self.client = routeoptimization_v1.RouteOptimizationClient()
        else:
            credentials = service_account.Credentials.from_service_account_info(json.loads(os.environ["GOOGLE_APPLICATION_CREDENTIALS"]))
            self.client = routeoptimization_v1.RouteOptimizationClient(credentials=credentials)

    def optimize(self, request: Dict[str, Any]):
        """
        Calls the OptimizeTours RPC using the provided fleet model payload.
        """
        request['parent'] = self.parent
        return self.client.optimize_tours(request=request)


class ObjectRouteOptimizer:
    """
    Coordinates the route optimization workflow: it prepares the payload that
    will be sent to Google Route Optimization, submits the request, and applies
    the optimizer response back into local Route / Order objects.
    """
    """
    to use partial optimization, the front end should send an object with key of " injected_first_solution_routes "
    with the following structure: 
    {
        "consider_route_trafic":false / true ( optional )
        "route_id": 12 ( mandatory )
        "partial_reoptimize": { ( optional )
            "injected_routes": [
            {
                "vehicle_label": "12-tiptapp",
                "visits": [
                { "shipment_label": "101-12" },
                { "shipment_label": "102-12" },
                { "shipment_label": "105-12" }   // new order added
                ]
            }
            ],
            
        }
    }
    notice that the vehicle_label is the route id and the route_label with a '-'.
    notice that the route_id is added to the route label with a '-' so it should be "order_id-route_id"

    """

    def __init__(self, response:"Response", identity=None):
        self.response = response
        self.identity = identity or getattr(response, "identity", None) or {}
        self.incoming_data: Dict[str, Any] = response.incoming_data or {}

        route_id = self.incoming_data.get("route_id")
        if not isinstance(route_id,int):
            if isinstance(route_id, str) and route_id.isdigit():
                route_id = int(route_id)
            else:
                route_id = None
        self.route_id:int = route_id
        self.consider_traffic = self.incoming_data.get('consider_traffic',False)
        self.apply_side_of_road = bool(self.incoming_data.get('side_of_road'))
        

        self.route: Optional[Route] = None
        self.orders: List[Order] = []
        self.order_lookup: Dict[int, Order] = {}
        self.order_stop_seconds: Dict[int, Optional[int]] = {}
        self.google_client: Optional[GoogleRouteOptimizationClient] = None
        self.route_start_time_iso: Optional[str] = None
        self.route_end_time_iso: Optional[str] = None
        self.skipped_shipments: List[Dict[str, Any]] = []
        self.optimization_summary: Dict[str, Any] = {}
        self.total_distance = 0
        self.total_duration = 0
        self.polylines_by_order = {}
        self.position = 0
        self.sequence = {}
        self.skipped_summary = []
        

    def optimize_route(self):
        if self.response.error:
            return False
        try:
            self._validate_payload()
            self._initialize_client()
            self._load_route()
            self._apply_route_overrides()
            self._apply_order_overrides()

            # incoming_data_example = {
            #     "route_id": 42,
            #     "consider_traffic": True,
            #     "side_of_road": True,
            #     "vehicle_id": 7,
            #     "route_modifiers": {
            #         "avoid_tolls": False,
            #         "avoid_highways": False,
            #         "avoid_ferries": False,
            #         "avoid_indoors": False,
            #     },
            #     "objectives": [{"type":{"MIN_TRAVEL_TIME": True}}],
            # }

            model_payload = self._build_request_model()
       
            api_response = self.google_client.optimize(model_payload)

            self._apply_optimizer_response(api_response)
            self._commit_and_set_payload()
            return True

        except Exception as exc:
            db.session.rollback()
            self.response.set_message("Error when optimizing the route.")
            self.response.set_error(str(exc), status=400)
            return False
        

    def _extract_shipment_label(self,obj:dict):
        raw_label:str = obj.get("shipment_label") or obj.get('label')
        if raw_label:
            split = raw_label.split('-')
            return split[0]
        return raw_label
    

    # # reviewing if need it....
    # def refresh_route_details(self, saved_route_indx = -1 ):
    #     """Refreshes route geometry and timing without re-optimizing."""
    #     last_opt = None
    #     if isinstance(self.route.saved_optimizations, list) and self.route.saved_optimizations:
    #         last_opt = self.route.saved_optimizations[saved_route_indx]  # use most recent
    #     if not last_opt:
    #         raise ValueError("No previous optimization available to refresh.")

    #     # Construct refresh model payload
    #     model_payload = {
    #         "refresh_details_routes": [last_opt],
    #         "populate_polylines": True,
    #         "consider_road_traffic": True,
    #         "interpret_injected_solutions_using_labels": True,
    #     }

    #     api_response = self.google_client.optimize(model_payload)
    #     self._apply_optimizer_response(api_response)
    #     self._commit_and_set_payload()

    def _validate_payload(self):
        if not isinstance(self.route_id, int):
            raise ValueError("route_id must be provided as an integer.")

    def _initialize_client(self):
        if not self.google_client:
            self.google_client = GoogleRouteOptimizationClient()

    def _load_route(self):
        self.route = GetObject.get_object(Route, self.route_id, identity=self.identity)
        self.orders = list(self.route.delivery_orders or [])
        if not self.orders:
            raise ValueError("Route has no orders to optimize.")
        # stable ordering
        self.orders.sort(
            key=lambda order: order.delivery_arrangement
            if order.delivery_arrangement is not None
            else float("inf")
        )
        self.order_lookup = {order.id: order for order in self.orders}

    def _apply_route_overrides(self):
        override_fields = ["set_start_time", "set_end_time", "start_location", "end_location"]
        for field in override_fields:
            if field in self.incoming_data:
                setattr(self.route, field, self.incoming_data[field])

        self.route_start_time_iso = self._resolve_datetime_string(
            self.route.set_start_time
        )
        self.route_end_time_iso = self._resolve_datetime_string(
            self.route.set_end_time 
        )
        self._apply_delivery_date_defaults()

    def _apply_delivery_date_defaults(self):
        if not getattr(self.route, "delivery_date", None):
            return
        delivery_date = self.route.delivery_date
        base_dt: Optional[datetime] = None
        if isinstance(delivery_date, datetime):
            base_dt = delivery_date
        else:
            parsed = str(delivery_date).strip()
            if parsed:
                try:
                    base_dt = datetime.fromisoformat(parsed)
                except ValueError:
                    base_dt = None
        if not base_dt:
            return
        if base_dt.tzinfo is None:
            base_dt = base_dt.replace(tzinfo=timezone.utc)
        base_dt = base_dt.astimezone(timezone.utc)

        if not self.route_start_time_iso:
            start_dt = datetime.combine(
                base_dt.date(),
                time_cls(hour=0, minute=0, second=0, tzinfo=timezone.utc),
            )
            self.route_start_time_iso = start_dt.isoformat().replace("+00:00", "Z")

        if not self.route_end_time_iso:
            end_dt = datetime.combine(
                base_dt.date(),
                time_cls(hour=23, minute=59, second=59, tzinfo=timezone.utc),
            )
            self.route_end_time_iso = end_dt.isoformat().replace("+00:00", "Z")

    # Correction, this could run at the same time as creating the request_build
    def _apply_order_overrides(self):
        overrides = self.incoming_data.get("orders", {}) or {}
        stop_time_data = overrides.get("stop_time")
        global_stop = None
        per_order: Dict[int, Any] = {}

        if isinstance(stop_time_data, dict):
            for key, value in stop_time_data.items():
                if key == "all":
                    global_stop = value
                else:
                    try:
                        per_order[int(key)] = value
                    except (TypeError, ValueError):
                        continue
        elif isinstance(stop_time_data, list):
            for entry in stop_time_data:
                if not isinstance(entry, dict):
                    continue
                entry_id = entry.get("id")
                if entry_id == "all":
                    global_stop = entry.get("stop_time")
                    continue
                if entry_id is None:
                    continue
                try:
                    per_order[int(entry_id)] = entry.get("stop_time")
                except (TypeError, ValueError):
                    continue
        elif stop_time_data is not None:
            # treat as "all"
            global_stop = stop_time_data

        if global_stop is not None:
            seconds = self._seconds_from_duration(global_stop)
            for order in self.orders:
                order.stop_time = str(seconds) if seconds is not None else order.stop_time
                self.order_stop_seconds[order.id] = seconds

        for order_id, value in per_order.items():
            order = self.order_lookup.get(order_id)
            if not order:
                continue
            seconds = self._seconds_from_duration(value)
            order.stop_time = str(seconds) if seconds is not None else order.stop_time
            self.order_stop_seconds[order_id] = seconds

        # ensure we have stop seconds for orders without overrides
        for order in self.orders:
            if order.id not in self.order_stop_seconds:
                seconds = self._seconds_from_duration(order.stop_time)
                self.order_stop_seconds[order.id] = seconds

    def _build_request_model(self) -> Dict[str, Any]:
       
        request = {}

        shipments = [self._build_shipment(order) for order in self.orders]
        vehicle = self._build_vehicle_definition()
        model: Dict[str, Any] = {
            "shipments": shipments,
            "vehicles": [vehicle],
        }
        if self.route_start_time_iso:
            model["global_start_time"] = self.route_start_time_iso
        if self.route_end_time_iso:
            model["global_end_time"] = self.route_end_time_iso
       
        request["model"] = model

        partial_reoptimize = self.incoming_data.get("partial_reoptimize")
        if partial_reoptimize:
            injected_routes = partial_reoptimize.get("injected_routes")
            if injected_routes:
                request["injected_first_solution_routes"] = injected_routes
                interpret_labels = partial_reoptimize.get(
                    "interpret_injected_solutions_using_labels", True
                )
                request["interpret_injected_solutions_using_labels"] = bool(interpret_labels)
        
        request["populate_transition_polylines"] = True


        return request

    def _build_objectives(self) -> List[Dict[str, Any]]:
        raw_objectives = self.incoming_data.get("objectives")
        if isinstance(raw_objectives, list) and raw_objectives:
            return raw_objectives
        if isinstance(raw_objectives, dict):
            return [raw_objectives]
        return list(DEFAULT_OBJECTIVES)

    def _build_shipment(self, order: Order) -> Dict[str, Any]:
        coords = self._coordinates_from_location(order.client_address)
        if not coords:
            raise ValueError(f"Order {order.id} is missing coordinates.")

        arrival_location = dict(coords)
        way_point = {
            "location": {'lat_lng':arrival_location}
        }
        if self.apply_side_of_road:
            way_point["side_of_road"] = True

        delivery: Dict[str, Any] = {
            "arrival_waypoint": way_point,
        }
        
        

        duration_seconds = self.order_stop_seconds.get(order.id)
        if duration_seconds:
            delivery["duration"] = self._format_duration(duration_seconds)

        time_windows = self._build_order_time_windows(order)
        if time_windows:
            delivery["time_windows"] = time_windows

        shipment = {
            "display_name": f"order-{order.id}-{self.route.id}",
            "label": f"{order.id}-{self.route.id}",
            "deliveries": [delivery],
        }
        return shipment

    def _build_vehicle_definition(self) -> Dict[str, Any]:
        start = self._coordinates_from_location(self.route.start_location)
        if not start:
            raise ValueError("Route is missing a valid start_location with coordinates.")
        end = self._coordinates_from_location(self.route.end_location) or start
        vehicle_template = self._resolve_vehicle_template()
        vehicle: Dict[str, Any] = {
            "display_name": f"vehicle-route-{self.route.id}-{self.route.route_label}",
            "label": f"{self.route.id}-{self.route.route_label}",
            "start_location": start,
            "end_location": end,
        }

        # if self.route_start_time_iso or self.route_end_time_iso:
        #     window: Dict[str, Any] = {}
        #     if self.route_start_time_iso:
        #         window["start_time"] = self.route_start_time_iso
        #     if self.route_end_time_iso:
        #         window["end_time"] = self.route_end_time_iso
        #     vehicle["start_time_windows"] = [window]

        # if self.route_end_time_iso:
        #     vehicle["end_time_windows"] = [{"end_time": self.route_end_time_iso}]

        vehicle["cost_per_kilometer"] = vehicle_template.get(
            "cost_per_kilometer", DEFAULT_VEHICLE_VALUES["cost_per_kilometer"]
        )
        vehicle["travel_mode"] = vehicle_template.get("travel_mode", DEFAULT_VEHICLE_VALUES["travel_mode"])
        
        overrides = {}

        for key in ("display_name", "label", "start_location", "end_location"):
            if vehicle_template.get(key):
                overrides[key] = vehicle_template[key]
        vehicle.update(overrides)
        vehicle["route_modifiers"] = self._resolve_route_modifiers(vehicle_template.get("route_modifiers"))

        return vehicle

    def _resolve_vehicle_template(self) -> Dict[str, Any]:
        template = dict(DEFAULT_VEHICLE_VALUES)
        template["route_modifiers"] = dict(DEFAULT_ROUTE_MODIFIERS)

        vehicle_id = self.incoming_data.get("vehicle_id")
        vehicle_instance = None
        if vehicle_id is not None:
            try:
                vehicle_instance = GetObject.get_object(UserVehicle, vehicle_id, identity=self.identity)
            except Exception:
                vehicle_instance = None

        if vehicle_instance:
            template.update(self._coerce_vehicle_record(vehicle_instance))

        return template

    def _coerce_vehicle_record(self, vehicle_instance: Any) -> Dict[str, Any]:
        allowed_keys = {
            "display_name",
            "label",
            "start_location",
            "end_location",
            "cost_per_kilometer",
            "fixed_cost",
            "travel_mode",
            "route_modifiers",
        }
        resolved: Dict[str, Any] = {}
        for key in allowed_keys:
            if hasattr(vehicle_instance, key):
                value = getattr(vehicle_instance, key)
                if value is not None:
                    resolved[key] = value
        return resolved

    def _resolve_route_modifiers(self, base: Optional[Dict[str, Any]] = None) -> Dict[str, bool]:
        modifiers = dict(DEFAULT_ROUTE_MODIFIERS)
        if isinstance(base, dict):
            for key, value in base.items():
                if key in modifiers:
                    modifiers[key] = bool(value)
        incoming = self.incoming_data.get("route_modifiers")
        if isinstance(incoming, dict):
            for key, value in incoming.items():
                if key in modifiers:
                    modifiers[key] = bool(value)
        return modifiers

    def _coordinates_from_location(self, location: Optional[Dict[str, Any]]):
        if not location:
            return None
        if "coordinates" in location and isinstance(location["coordinates"], dict):
            candidate = location["coordinates"]
        else:
            candidate = location
        lat = (
            candidate.get("lat")
            or candidate.get("latitude")
            or candidate.get("Lat")
            or candidate.get("Latitude")
        )
        lng = (
            candidate.get("lng")
            or candidate.get("lon")
            or candidate.get("longitude")
            or candidate.get("Lng")
            or candidate.get("Longitude")
        )
        if lat is None or lng is None:
            return None
        try:
            return {"latitude": float(lat), "longitude": float(lng)}
        except (TypeError, ValueError):
            return None

    def _build_order_time_windows(self, order: Order) -> List[Dict[str, str]]:
        windows = []
        start = self._resolve_datetime_string(order.delivery_after)
        end = self._resolve_datetime_string(order.delivery_before)
        if start or end:
            window: Dict[str, str] = {}
            if start:
                window["start_time"] = start
            if end:
                window["end_time"] = end
            windows.append(window)
        return windows

    def _resolve_datetime_string(self, value) -> Optional[str]:
        if not value:
            return None
        dt: Optional[datetime] = None
        if isinstance(value, datetime):
            dt = value
        else:
            parsed = str(value).strip()
            if parsed.endswith("Z"):
                parsed = parsed[:-1] + "+00:00"
            try:
                dt = datetime.fromisoformat(parsed)
            except ValueError:
                if ":" in parsed:
                    parts = parsed.split(":")
                    try:
                        hour = int(parts[0])
                        minute = int(parts[1])
                        second = int(parts[2]) if len(parts) > 2 else 0
                        base_date = self.route.delivery_date or datetime.now(timezone.utc)
                        base_date = base_date.astimezone(timezone.utc)
                        dt = datetime.combine(
                            base_date.date(),
                            time_cls(hour=hour, minute=minute, second=second, tzinfo=timezone.utc),
                        )
                    except ValueError:
                        dt = None
        if not dt:
            return None
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

    def _seconds_from_duration(self, value) -> Optional[int]:
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return int(value)
        parsed = str(value).strip().lower()
        if not parsed:
            return None

        suffix_map = {
            "s": 1,
            "sec": 1,
            "secs": 1,
            "second": 1,
            "seconds": 1,
            "m": 60,
            "min": 60,
            "mins": 60,
            "minute": 60,
            "minutes": 60,
            "h": 3600,
            "hr": 3600,
            "hrs": 3600,
            "hour": 3600,
            "hours": 3600,
        }
        for suffix, multiplier in suffix_map.items():
            if parsed.endswith(suffix):
                numeric = parsed[: -len(suffix)].strip()
                try:
                    return int(float(numeric) * multiplier)
                except ValueError:
                    return None

        if ":" in parsed:
            try:
                parts = [int(part) for part in parsed.split(":")]
                while len(parts) < 3:
                    parts.append(0)
                hours, minutes, seconds = parts[:3]
                return hours * 3600 + minutes * 60 + seconds
            except ValueError:
                return None

        try:
            return int(float(parsed))
        except ValueError:
            return None

    def _format_duration(self, seconds: Optional[int]) -> Optional[str]:
        if seconds is None:
            return None
        return f"{int(seconds)}s"

    def _seconds_from_duration_string(self, value) -> int:
        if value is None:
            return 0
        if isinstance(value, dict):
            seconds = int(value.get("seconds", 0))
            nanos = int(value.get("nanos", 0))
            return seconds + int(nanos / 1_000_000_000)
        return self._seconds_from_duration(value) or 0

    def _apply_optimizer_response(self, api_response):

        message = getattr(api_response, "_pb", api_response)
        response_dict = MessageToDict(message, preserving_proto_field_name=True)


        routes = response_dict.get("routes", [])
        if not routes:
            raise ValueError("Route Optimization API returned no routes.")

        optimized_route: dict = routes[0]

        visits: list[dict] = optimized_route.get("visits", [])
        transitions = optimized_route.get("transitions", [])
        
        # extracts the transitions between orders ( steps )
        self._extract_transitions( transitions, visits )
        
        # extracts the visits ( actual order optimized info )
        self._extract_visits( visits )
       
        # extracts the shipments that where skipped
        skipped = response_dict.get("skipped_shipments", [])

        self._extract_skipped_shipments(skipped)
       

        expected_start = (
            optimized_route.get("vehicle_start_time")
            or (visits[0].get("arrival_time") if visits else None)
            or self.route_start_time_iso
        )
        expected_end = (
            optimized_route.get("vehicle_end_time")
            or (
                (visits[-1].get("departure_time") or visits[-1].get("arrival_time"))
                if visits
                else None
            )
            or self.route_end_time_iso
        )

        self.route.expected_start_time = expected_start or self.route.expected_start_time
        self.route.expected_end_time = expected_end or self.route.expected_end_time
        self.route.is_optimized = True

        route_saved_optimizations = list(self.route.saved_optimizations or []) 
        self.skipped_shipments = self.skipped_summary
        self.optimization_summary = {
            "total_distance_meters": self.total_distance,
            "total_duration_seconds": self.total_duration,
            "expected_start_time": self.route.expected_start_time,
            "expected_end_time": self.route.expected_end_time,
            "set_start_time": self.route.set_start_time,
            "set_end_time": self.route.set_end_time,
            "start_location": self.route.start_location,
            "end_location": self.route.end_location,
            "order_sequence": self.sequence,
            "skipped_shipments": self.skipped_summary,
            "polylines": self.polylines_by_order,
            "consider_traffic":self.consider_traffic
        }
        route_saved_optimizations.append(self.optimization_summary)
        if len(route_saved_optimizations) > 3:
            route_saved_optimizations = route_saved_optimizations[-3:]
        self.route.saved_optimizations = route_saved_optimizations
        self.route.using_optimization_indx = len(route_saved_optimizations) - 1 


   
    def _extract_transitions(self, transitions, visits ):


        for idx, transition in enumerate(transitions):
           
            trans_polyline = None
            route_polyline = None

            if isinstance(transition, dict):
                self.total_distance += transition.get("travel_distance_meters", 0)
                self.total_duration += self._seconds_from_duration_string(transition.get("travel_duration"))
                route_polyline = transition.get("route_polyline")


            if isinstance(route_polyline, dict):
                trans_polyline = route_polyline.get("points")
            elif isinstance(route_polyline, str):
                trans_polyline = route_polyline
            
            
            if idx == 0:
                # First transition: from start to first order
                self.polylines_by_order["start"] = trans_polyline
                if len(visits) > 0:
                    first_label = self._extract_shipment_label(visits[0])
                    if first_label:
                        try:
                            next_id = int(first_label)
                            self.polylines_by_order[str(next_id)] = trans_polyline
                        except Exception:
                            pass
            elif idx == len(transitions) - 1:
                # Last transition: from last order to end
                self.polylines_by_order["end"] = trans_polyline
                if len(visits) > idx:
                    last_label = self._extract_shipment_label(visits[idx])
                    if last_label:
                        try:
                            next_id = int(last_label)
                            self.polylines_by_order[str(next_id)] = trans_polyline
                        except Exception:
                            pass
            else:
                # Transition from visits[idx] to visits[idx+1]
                if len(visits) > idx :

                    next_label = self._extract_shipment_label(visits[idx])

                    if next_label:
                        try:
                            next_id = int(next_label)
                            self.polylines_by_order[str(next_id)] = trans_polyline
                        except Exception:
                            pass

        
    def _extract_visits(self, visits):
        for idx, visit in enumerate(visits):
            shipment_label = self._extract_shipment_label(visit)
            if not shipment_label:
                continue
            try:
                order_id = int(shipment_label)
            except (TypeError, ValueError):
                continue
            order = self.order_lookup.get(order_id)
            if not order:
                continue

            
            order.delivery_arrangement = self.position
            sequence_obj = { "delivery_arrangement": self.position, "in_range":True }
            order.in_range = True
            self.position += 1
            arrival_time = visit.get("arrival_time") or visit.get("start_time")
            sequence_obj['expected_arrival_time'] = arrival_time
            if arrival_time:
                order.expected_arrival_time = arrival_time

            self.sequence[order_id] = sequence_obj
            # Do NOT set order.delivery_polyline here

    def _extract_skipped_shipments(self, skipped):
        skipped_position = self.position
        for shipment in skipped:

            shipment_label = self._extract_shipment_label(shipment)
            if not shipment_label:
                continue
            try:
                order_id = int(shipment_label)
            except (TypeError, ValueError):
                continue
            order = self.order_lookup.get(order_id)
            if not order:
                continue
            order.delivery_arrangement = skipped_position
            order.in_range = False
            skipped_position += 1
            order.expected_arrival_time = None
            skipped_entry = {
                "order_id": order_id,
                "reason": shipment.get("reasons", "UNSPECIFIED"),
            }
            self.skipped_summary.append(skipped_entry)


    def _serialize_route(self) -> Dict[str, Any]:
        return {
            "id": self.route.id,
            "route_label": self.route.route_label,
            "expected_start_time": self.route.expected_start_time,
            "expected_end_time": self.route.expected_end_time,
            "set_start_time": self.route.set_start_time,
            "set_end_time": self.route.set_end_time,
            "start_location": self.route.start_location,
            "end_location": self.route.end_location,
            "is_optimized": self.route.is_optimized,
            'saved_optimizations':self.optimization_summary,
            'using_optimization_indx':self.route.using_optimization_indx,
            "delivery_orders": [self._serialize_order(order) for order in self.orders]

        }

    def _serialize_order(self, order: Order) -> Dict[str, Any]:
        return {
            "id": order.id,
            "delivery_arrangement": order.delivery_arrangement,
            "expected_arrival_time": order.expected_arrival_time,
            "stop_time": order.stop_time,
            "in_range": order.in_range,
        }

    def _commit_and_set_payload(self):

        db.session.add(self.route)
        db.session.add_all(self.orders)
        db.session.commit()

        payload = {
            "route": self._serialize_route(),
        }

        self.response.set_payload(payload)
        self.response.set_message("Route optimized successfully.")
        # self.response.compress_payload()
