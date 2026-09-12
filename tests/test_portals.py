"""Tests for Presentation Layer Portals & Security Guards."""

import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_public_routes(client):
    res = client.get("/")
    assert res.status_code == 200

    res = client.get("/about")
    assert res.status_code == 200


def test_legacy_portal_redirects(client):
    for route in ["/portal", "/cos", "/l2-cos", "/dashboard", "/admin"]:
        res = client.get(route)
        assert res.status_code == 302
        assert "/operations" in res.headers["Location"]


def test_driver_portal_unauthorized_without_pin(client):
    res = client.get("/driver")
    assert res.status_code == 401


def test_driver_portal_authorized_with_pin(client):
    res = client.get("/driver", headers={"X-Driver-PIN": "1234"})
    assert res.status_code == 200


def test_operations_portal(client):
    res = client.get("/operations")
    assert res.status_code == 200


def test_stakeholder_portal_sanitization(client):
    res = client.get("/stakeholder?role=Customer")
    assert res.status_code == 200
    assert b"Broker" not in res.data or b"Customer" in res.data


def test_operations_card_action(client):
    res = client.get("/api/v1/operations/cards")
    assert res.status_code == 200
    cards = res.get_json()
    assert len(cards) > 0

    card_id = cards[0]["card_id"]
    action = cards[0]["allowed_actions"][0]

    action_res = client.post("/api/v1/operations/action", json={
        "card_id": card_id,
        "action": action
    })
    assert action_res.status_code == 200
    assert action_res.get_json()["status"] == "success"
