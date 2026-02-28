from types import SimpleNamespace

from Delivery_app_BK.services.commands.auth import refresh_socket_token as module


def test_refresh_socket_token_preserves_timezone_claim(monkeypatch):
    captured = {}

    def _fake_create_access_token(identity, additional_claims, expires_delta=None):
        captured["identity"] = identity
        captured["claims"] = additional_claims
        captured["expires_delta"] = expires_delta
        return "socket-token"

    monkeypatch.setattr(module, "create_access_token", _fake_create_access_token)

    result = module.refresh_socket_token(
        SimpleNamespace(
            identity={
                "user_id": 3,
                "team_id": 5,
                "user_role_id": 7,
                "base_role_id": 11,
                "time_zone": "Europe/Stockholm",
            }
        )
    )

    assert result == {"socket_token": "socket-token"}
    assert captured["identity"] == "3"
    assert captured["claims"]["time_zone"] == "Europe/Stockholm"
    assert captured["expires_delta"] is not None


def test_refresh_socket_token_falls_back_to_utc_for_legacy_claims(monkeypatch):
    captured = {}

    def _fake_create_access_token(identity, additional_claims, expires_delta=None):
        captured["claims"] = additional_claims
        return "socket-token"

    monkeypatch.setattr(module, "create_access_token", _fake_create_access_token)

    module.refresh_socket_token(
        SimpleNamespace(
            identity={
                "user_id": 3,
                "team_id": 5,
                "user_role_id": 7,
                "base_role_id": 11,
            }
        )
    )

    assert captured["claims"]["time_zone"] == "UTC"
