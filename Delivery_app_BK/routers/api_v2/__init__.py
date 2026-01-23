from .item import item_bp
from .label_template import label_template_bp
from .message_template import message_template_bp
from .plan import plan_bp
from .order import order_bp
from .infrastructure import infrastructure_bp
from .external_integration import external_integration_bp
from .notification import notification_bp
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



def register_v2_blueprints(app):
    app.register_blueprint(item_bp, url_prefix="/api_v2/items")
    app.register_blueprint(label_template_bp, url_prefix="/api_v2/label_templates")
    app.register_blueprint(message_template_bp, url_prefix="/api_v2/message_templates")
    app.register_blueprint(plan_bp, url_prefix="/api_v2/plans")
    app.register_blueprint(order_bp, url_prefix="/api_v2/orders")
    app.register_blueprint(infrastructure_bp, url_prefix="/api_v2/infrastructures")
    app.register_blueprint(
        external_integration_bp,
        url_prefix="/api_v2/external_integrations",
    )
    app.register_blueprint(notification_bp, url_prefix="/api_v2/notifications")
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
