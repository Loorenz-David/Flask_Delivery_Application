from Delivery_app_BK.models import db, OrderEventAction

# will be async in the future when we have async workers, but for now we can run it synchronously since email sending is fast and we want to ensure it happens before the response is sent back to the client
def sync_shopify(action_id: int) -> None:
    action = db.session.get(OrderEventAction, action_id)
    if action is None:
        return

    action.attempts = (action.attempts or 0) + 1
    action.status = OrderEventAction.STATUS_SUCCESS
    action.last_error = None
    db.session.commit()
