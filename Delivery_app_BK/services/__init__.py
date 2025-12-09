from Delivery_app_BK.services.general_services.general_creation import create_general_object
from Delivery_app_BK.services.general_services.general_deletion import delete_general_object


from Delivery_app_BK.services.item_services.service_create import service_create_item_category
from Delivery_app_BK.services.item_services.service_create import service_create_item_type
from Delivery_app_BK.services.item_services.service_create import service_create_item_property
from Delivery_app_BK.services.item_services.service_create import service_create_item
from Delivery_app_BK.services.item_services.service_create import service_create_item_state
from Delivery_app_BK.services.item_services.service_create import service_create_item_position
from Delivery_app_BK.services.item_services.service_query_options import service_query_item_options
from Delivery_app_BK.services.order_services.service_create import service_create_order
from Delivery_app_BK.services.routes_services.service_create import service_create_route
from Delivery_app_BK.services.routes_services.service_optimize import service_optimize_route
from Delivery_app_BK.services.notifications_services.service_create import service_create_email_smtp
from Delivery_app_BK.services.notifications_services.service_create import service_create_twilio_mod
from Delivery_app_BK.services.notifications_services.service_create import service_create_message_template
from Delivery_app_BK.services.user_services.service_create import (
    service_create_user,
    service_create_team,
    service_create_user_role,
    service_create_user_warehouse,
)


from Delivery_app_BK.services.item_services.service_update import (
    service_update_item,
    service_update_item_category,
    service_update_item_type,
    service_update_item_property,
    service_update_item_state,
    service_update_item_position,
)
from Delivery_app_BK.services.item_services.service_delete import (
    service_delete_item,
    service_delete_item_category,
    service_delete_item_type,
    service_delete_item_property,
    service_delete_item_state,
    service_delete_item_position,
)
from Delivery_app_BK.services.routes_services.service_update import service_update_route
from Delivery_app_BK.services.routes_services.service_delete import service_delete_route
from Delivery_app_BK.services.order_services.service_update import service_update_order
from Delivery_app_BK.services.order_services.service_delete import service_delete_order
from Delivery_app_BK.services.notifications_services.service_update import service_update_email_smtp
from Delivery_app_BK.services.notifications_services.service_update import service_update_twilio_mod
from Delivery_app_BK.services.notifications_services.service_update import service_update_message_template
from Delivery_app_BK.services.notifications_services.service_delete import (
    service_delete_email_smtp,
    service_delete_twilio_mod,
    service_delete_message_template,
)
from Delivery_app_BK.services.user_services.service_update import (
    service_update_user,
    service_update_team,
    service_update_user_role,
    service_update_user_warehouse,
)
from Delivery_app_BK.services.user_services.service_delete import (
    service_delete_user,
    service_delete_team,
    service_delete_user_role,
    service_delete_user_warehouse,
)
