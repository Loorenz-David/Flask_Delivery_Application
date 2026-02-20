from Delivery_app_BK.services.infra.tasks.delivery_plan.send_email import send_email
from ._actions import run_action

def send_email_on_plan_delivery_rescheduled(plan_event) -> None:
    run_action(plan_event, "plan_delivery_rescheduled_email", send_email)
