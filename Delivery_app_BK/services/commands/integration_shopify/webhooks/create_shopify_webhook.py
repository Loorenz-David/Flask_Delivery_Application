import requests
from Delivery_app_BK.errors import ValidationFailed

def create_shopify_webhook(shop, access_token, topic, address):
    url = f"https://{shop}/admin/api/2024-01/webhooks.json"

    headers = {
        "X-Shopify-Access-Token": access_token,
        "Content-Type": "application/json",
    }

    payload = {
        "webhook": {
            "topic": topic,
            "address": address,
            "format": "json",
        }
    }

    response = requests.post(url, json=payload, headers=headers, timeout=10)
  
    if response.status_code not in (200, 201):
        raise ValidationFailed("Failed to create Shopify webhook")

    return response.json()