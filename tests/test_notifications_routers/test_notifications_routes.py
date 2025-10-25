import base64
import gzip
import json

from Delivery_app_BK.models import EmailSMTP, MessageTemplate, TwilioMod


def compress_payload(payload: dict) -> dict:
    compressed = gzip.compress(json.dumps(payload).encode("utf-8"))
    return {"is_compress": True, "data": base64.b64encode(compressed).decode("utf-8")}


def decode_response_payload(response_json: dict) -> dict:
    assert response_json["is_compress"] is True
    compressed = base64.b64decode(response_json["data"])
    return json.loads(gzip.decompress(compressed).decode("utf-8"))


def seed_email_config(client, app, headers) -> EmailSMTP:
    res = client.post(
        "/notifications/create_email_smtp",
        json={
            "smtp_server": "smtp.example.com",
            "smtp_username": "mailer",
            "smtp_password_encrypted": "encrypted",
            "use_tls": True,
        },
        headers=headers,
    )
    assert res.status_code == 200
    with app.app_context():
        config = EmailSMTP.query.first()
        assert config is not None
        return config


def seed_twilio_config(client, app, headers) -> TwilioMod:
    res = client.post(
        "/notifications/create_twilio_mod",
        json={
            "twilio_sid": "sid",
            "twilio_token_encrypted": "token",
            "sender_number": "+123456789",
        },
        headers=headers,
    )
    assert res.status_code == 200
    with app.app_context():
        config = TwilioMod.query.first()
        assert config is not None
        return config


def seed_message_template(client, app, headers, name: str = "Welcome") -> MessageTemplate:
    res = client.post(
        "/notifications/create_message_template",
        json={
            "content": "Hello there!",
            "name": name,
            "channel": "email",
        },
        headers=headers,
    )
    assert res.status_code == 200
    with app.app_context():
        template = MessageTemplate.query.filter_by(name=name).first()
        assert template is not None
        return template


def test_create_notification_resources(client, app, auth_headers):
    email_config = seed_email_config(client, app, auth_headers)
    twilio_config = seed_twilio_config(client, app, auth_headers)
    template = seed_message_template(client, app, auth_headers)

    with app.app_context():
        assert EmailSMTP.query.get(email_config.id) is not None
        assert TwilioMod.query.get(twilio_config.id) is not None
        assert MessageTemplate.query.get(template.id) is not None


def test_update_email_smtp_supports_compressed_payload(client, app, auth_headers):
    config = seed_email_config(client, app, auth_headers)

    update_payload = {
        "id": config.id,
        "fields": {
            "smtp_port": 465,
            "use_ssl": True,
        },
    }

    res = client.put(
        "/notifications/update_email_smtp",
        json=compress_payload(update_payload),
        headers=auth_headers,
    )
    assert res.status_code == 200
    assert "Email SMTP configuration updated successfully" in res.get_json()["message"]

    with app.app_context():
        updated_config = EmailSMTP.query.get(config.id)
        assert updated_config.smtp_port == 465
        assert updated_config.use_ssl is True


def test_query_message_template_returns_expected_payload(client, app, auth_headers):
    seed_message_template(client, app, auth_headers, name="Reminder")

    query_payload = {
        "query": {"name": {"operation": "==", "value": "Reminder"}},
        "requested_data": ["id", "name", "channel"],
    }

    res = client.post(
        "/notifications/query_message_template",
        json=compress_payload(query_payload),
        headers=auth_headers,
    )
    assert res.status_code == 200

    body = res.get_json()
    unpacked = decode_response_payload(body)
    assert "items" in unpacked
    assert len(unpacked["items"]) == 1
    assert unpacked["items"][0]["name"] == "Reminder"
