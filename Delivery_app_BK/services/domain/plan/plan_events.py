from enum import Enum


class DeliveryPlanEvent(str, Enum):
    DELIVERY_PLAN_RESCHEDULED = "delivery_plan_rescheduled"


class planEventPrintDocuments(str, Enum):
    ROUTE_SOLUTION_FOR_PRINTING = "route_solution_for_printing"