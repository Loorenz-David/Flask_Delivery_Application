from Delivery_app_BK.models.managers.object_route_optimizer import (
    ObjectRouteOptimizer,
)


def service_optimize_route(response, identity=None):
    """
    Orchestrates the optimization flow by delegating to ObjectRouteOptimizer.
    """
    optimizer = ObjectRouteOptimizer(response=response, identity=identity)
    optimizer.optimize_route()
    return optimizer
