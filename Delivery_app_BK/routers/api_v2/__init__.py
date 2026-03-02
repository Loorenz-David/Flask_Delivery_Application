from .item import item_bp
from .label_template import label_template_bp
from .message_template import message_template_bp
from .plan import plan_bp
from .order import order_bp
from .infrastructure import infrastructure_bp
from .external_integration import external_integration_bp
from .order_case import order_case_bp
from .user_role import user_role_bp
from .user_role_rule import user_role_rule_bp
from .user import user_bp
from .user_registration import user_registration_bp
from .team_members import team_bp
from .team_invitation import team_invitation_bp
from .auth import auth_bp
from .seed import seed_bp
from .bootstrap import bootstrap_bp
from .integration_shopify import shopify_bp
from .integrations import integrations_bp
from .integration_twilio import twilio_bp
from .integration_email import email_bp
from .item_type import item_type_bp
from .item_property import item_property_bp
from .route_solution import route_solution_bp
from .plan_overviews import plan_overviews_bp
from .item_position import item_position_bp
from .item_state import item_state_bp
from .costumer import costumer_bp




def register_v2_blueprints(app):
    app.register_blueprint(item_bp, url_prefix="/api_v2/items")
    app.register_blueprint(item_type_bp, url_prefix="/api_v2/item_types")
    app.register_blueprint(item_property_bp, url_prefix="/api_v2/item_properties")
    app.register_blueprint(item_position_bp, url_prefix="/api_v2/item_positions")
    app.register_blueprint(item_state_bp, url_prefix="/api_v2/item_states")

    app.register_blueprint(label_template_bp, url_prefix="/api_v2/label_templates")
    app.register_blueprint(message_template_bp, url_prefix="/api_v2/message_templates")
    app.register_blueprint(plan_bp, url_prefix="/api_v2/plans")
    app.register_blueprint(order_bp, url_prefix="/api_v2/orders")
    app.register_blueprint(infrastructure_bp, url_prefix="/api_v2/infrastructures")
    app.register_blueprint(
        external_integration_bp,
        url_prefix="/api_v2/external_integrations",
    )
    app.register_blueprint(order_case_bp, url_prefix="/api_v2/order_cases")
    app.register_blueprint(user_role_bp, url_prefix="/api_v2/user_roles")
    app.register_blueprint(user_role_rule_bp, url_prefix="/api_v2/user_role_rules")
    app.register_blueprint(user_bp, url_prefix="/api_v2/users")
    app.register_blueprint(user_registration_bp, url_prefix="/api_v2/user_registration")
    app.register_blueprint(team_bp, url_prefix="/api_v2/teams")
    app.register_blueprint(team_invitation_bp, url_prefix="/api_v2/team_invitations")
    app.register_blueprint(auth_bp, url_prefix="/api_v2/auths")
    app.register_blueprint(seed_bp, url_prefix="/api_v2/seed")
    app.register_blueprint(bootstrap_bp, url_prefix="/api_v2/bootstrap")
    app.register_blueprint(shopify_bp, url_prefix="/api_v2/shopify")
    app.register_blueprint(integrations_bp,url_prefix="/api_v2/integrations")
    app.register_blueprint(twilio_bp,url_prefix="/api_v2/twilio")
    app.register_blueprint(email_bp,url_prefix="/api_v2/email")
    app.register_blueprint(route_solution_bp, url_prefix="/api_v2/route_solutions")
    app.register_blueprint(plan_overviews_bp, url_prefix="/api_v2/plan_overviews")
    app.register_blueprint(costumer_bp, url_prefix="/api_v2/costumers")
