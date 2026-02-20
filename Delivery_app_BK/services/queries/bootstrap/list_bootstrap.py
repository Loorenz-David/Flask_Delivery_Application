from ...context import ServiceContext
from ..item_state.list_item_states import list_item_states
from ..order_states.list_order_states import list_order_states
from ..plan_states.list_plan_states import list_plan_states
from ..team_members.list_team_members import list_team_members
from ..content_templates.label.list_label_templates import list_label_templates_bootstrap
from ..content_templates.messages.list_message_templates import list_message_templates_bootstrap

def list_bootstrap(ctx: ServiceContext):
    ctx.query_params = {}
    payload = {}
    payload["team_members"] = list_team_members(ctx)["team_members"]
    payload["item_states"] = list_item_states(ctx)["item_states"]
    
    payload["order_states"] = list_order_states(ctx)["order_states"]
    payload["plan_states"] = list_plan_states(ctx)["plan_states"]
    payload['label_templates'] = list_label_templates_bootstrap(ctx)['label_templates']
    
    ctx.query_params = {"channel":'email'}
    payload['message_templates_email'] = list_message_templates_bootstrap(ctx)['message_templates']
    ctx.query_params = {"channel":'sms'}
    payload['message_templates_sms'] = list_message_templates_bootstrap(ctx)['message_templates']
    

    return payload
