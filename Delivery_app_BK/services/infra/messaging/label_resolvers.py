from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Callable

from Delivery_app_BK.models import RouteSolution, RouteSolutionStop, db

if TYPE_CHECKING:
    from Delivery_app_BK.models import DeliveryPlanEvent, Order, OrderEvent


class MessageRenderContext:
    def __init__(
        self,
        order: "Order",
        order_event: "OrderEvent | None" = None,
        team_id: int | None = None,
        delivery_plan_event: "DeliveryPlanEvent | None" = None,
    ) -> None:
        self.order = order
        self.order_event = order_event
        self.delivery_plan_event = delivery_plan_event
        self.team_id = team_id
        self._selected_route_stop_loaded = False
        self._selected_route_stop: RouteSolutionStop | None = None

    def get_selected_route_stop(self) -> RouteSolutionStop | None:
        if self._selected_route_stop_loaded:
            return self._selected_route_stop

        query = (
            db.session.query(RouteSolutionStop)
            .join(RouteSolution, RouteSolutionStop.route_solution_id == RouteSolution.id)
            .filter(
                RouteSolutionStop.order_id == self.order.id,
                RouteSolution.is_selected.is_(True),
            )
            .order_by(RouteSolutionStop.stop_order.asc(), RouteSolutionStop.id.asc())
        )

        if self.team_id is not None:
            query = query.filter(
                RouteSolutionStop.team_id == self.team_id,
                RouteSolution.team_id == self.team_id,
            )

        self._selected_route_stop = query.first()
        self._selected_route_stop_loaded = True
        return self._selected_route_stop


LabelResolver = Callable[[MessageRenderContext, str], str]


def _to_string(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return str(value)


def _resolve_client_first_name(context: MessageRenderContext, channel: str) -> str:
    return _to_string(getattr(context.order, "client_first_name", None))


def _resolve_client_last_name(context: MessageRenderContext, channel: str) -> str:
    return _to_string(getattr(context.order, "client_last_name", None))


def _resolve_tracking_number(context: MessageRenderContext, channel: str) -> str:
    return _to_string(getattr(context.order, "tracking_number", None))


def _resolve_plan_delivery_date_display(context: MessageRenderContext, channel: str) -> str:
    delivery_plan_event = context.delivery_plan_event
    if delivery_plan_event is None:
        return ""
    delivery_plan = delivery_plan_event.delivery_plan
    if delivery_plan is None:
        return ""

    start_date = getattr(delivery_plan, "start_date", None)
    end_date = getattr(delivery_plan, "end_date", None)
    if not isinstance(start_date, datetime) or not isinstance(end_date, datetime):
        return ""
    
    if start_date.date() == end_date.date():
        return start_date.strftime("%Y-%m-%d")
    else:
        return f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"  






def _resolve_expected_arrival_time(context: MessageRenderContext, channel: str, range_minutes: int = 0) -> str:
    stop = context.get_selected_route_stop()
    if stop is None:
        return ""

    arrival_time = getattr(stop, "expected_arrival_time", None)
    if not isinstance(arrival_time, datetime):
        return ""
    
    # Round to nearest 30 minutes
    from datetime import timedelta

    minute = arrival_time.minute
    if minute < 15:
        rounded_minute = 0
    elif minute < 45:
        rounded_minute = 30
    else:
        arrival_time = arrival_time + timedelta(hours=1)
        rounded_minute = 0

    arrival_time = arrival_time.replace(minute=rounded_minute, second=0, microsecond=0)

    if range_minutes > 0:

        start_time = arrival_time - timedelta(minutes=range_minutes)
        end_time = arrival_time + timedelta(minutes=range_minutes)
        return (
            start_time.strftime("%Y-%m-%d") + " " + start_time.strftime("%H:%M")
            + " to "
            + end_time.strftime("%Y-%m-%d") + " " + end_time.strftime("%H:%M")
        )
    return arrival_time.strftime("%Y-%m-%d") + " " + arrival_time.strftime("%H:%M")

def _resolve_tracking_link(context: MessageRenderContext, channel: str) -> str:
    return _to_string(getattr(context.order, "tracking_link", None))


def phone_to_string(phone_data: object) -> str:
    if isinstance(phone_data, str):
        return phone_data
    
    if isinstance(phone_data, dict):
        prefix = phone_data.get("prefix")
        if isinstance(prefix, str):
            number = phone_data.get("number")
            if isinstance(number, str):
                return f"{prefix}{number}"
        number = phone_data.get("number")
        if isinstance(number, str):
            return number
    return ""

def _resolve_client_phone_number(context: MessageRenderContext, channel: str, is_secondary: bool = False) -> str:
    primary_phone_data = getattr(context.order, "client_primary_phone", None)
    secondary_phone_data = getattr(context.order, "client_secondary_phone", None)
    if primary_phone_data is None and secondary_phone_data is None:
        return ""
    if is_secondary:
        return phone_to_string(secondary_phone_data)
    return phone_to_string(primary_phone_data)
   
    return ""

def _resolve_client_address(context: MessageRenderContext, channel: str) -> str:
    address_data = getattr(context.order, "client_address", None)
    if not isinstance(address_data, dict):
        return ""
    
    address_lines = []
    street = address_data.get("street_address")
    if isinstance(street, str) and street:
        return str(street)
    postal_code = address_data.get("postal_code")
    if isinstance(postal_code, str) and postal_code:
        address_lines.append(postal_code)
    state = address_data.get("state")
    if isinstance(state, str) and state:
        address_lines.append(state)
    city = address_data.get("city")
    if isinstance(city, str) and city:
        address_lines.append(city)
    country = address_data.get("country")
    if isinstance(country, str) and country:
        address_lines.append(country)
    
    return ", ".join(address_lines)



LABEL_RESOLVER_REGISTRY: dict[str, LabelResolver] = {
    "client_first_name": _resolve_client_first_name,
    "client_last_name": _resolve_client_last_name,
    "tracking_number": _resolve_tracking_number,
    "tracking_link": _resolve_tracking_link,

    "expected_arrival_time_with_range_30": lambda context, channel: _resolve_expected_arrival_time(context, channel, 30),
    "expected_arrival_time": _resolve_expected_arrival_time,
    "client_phone_number": _resolve_client_phone_number,
    "client_phone_number_secondary": lambda context, channel: _resolve_client_phone_number(context, channel, is_secondary=True),
    "client_address": _resolve_client_address,
    "plan_delivery_date_display":_resolve_plan_delivery_date_display,
}


def resolve_label(label_key: str, context: MessageRenderContext, channel: str) -> str:
    resolver = LABEL_RESOLVER_REGISTRY.get(label_key)
    if resolver is None:
        return ""
    return _to_string(resolver(context, channel))
