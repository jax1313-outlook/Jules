"""
Unit and Integration Tests for Dispatch Presentation Layers and API Endpoints
"""

import pytest
from app import app
from dispatch_spine import spine_store, LEVEL_3_DECISION, LEVEL_4_CONFLICT, LEVEL_5_AUTHORITY

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_public_website_routes(client):
    """Test public website routes respond with status 200 and expected branding."""
    routes = [
        ('/', 'Jacksonville Regional Micro-Response Carrier'),
        ('/about', 'About Level 1 Transport'),
        ('/capabilities', 'Precision Micro-Response Fleet Capabilities'),
        ('/contact', 'Contact Level 1 Transport')
    ]
    for url, text_snippet in routes:
        response = client.get(url)
        assert response.status_code == 200
        assert text_snippet.encode('utf-8') in response.data

def test_driver_portal_route(client):
    """Test Driver Portal renders truck-cab cockpit data."""
    response = client.get('/driver')
    assert response.status_code == 200
    assert b'DRIVER PORTAL' in response.data
    assert b'Active Trip Card' in response.data
    assert b'L1T-2026-8804' in response.data

def test_operations_portal_route(client):
    """Test Operations Portal renders decision cards and work queues."""
    response = client.get('/operations')
    assert response.status_code == 200
    assert b'OPERATIONS / MANAGEMENT PORTAL' in response.data
    assert b'Dispatch Work Queue' in response.data
    assert b'LEVEL 3: MIKE DECISION' in response.data

def test_stakeholder_portal_route(client):
    """Test External Stakeholder Portal renders sanitized confidence window."""
    response = client.get('/stakeholder?ref=L1T-2026-8804')
    assert response.status_code == 200
    assert b'EXTERNAL STAKEHOLDER PORTAL' in response.data
    assert b'Jacksonville Marine Terminal Pier 4' in response.data

def test_driver_load_search_api(client):
    """Test operational load search API."""
    response = client.get('/api/v1/driver/search-loads?q=Savannah')
    assert response.status_code == 200
    data = response.get_json()
    assert data['count'] > 0
    assert data['results'][0]['load_number'] == 'L1T-2026-8804'

def test_driver_pod_upload_api(client):
    """Test POD upload API trigger."""
    response = client.post('/api/v1/driver/upload-pod')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert data['pod_status'] == 'UPLOADED'

def test_operations_action_api(client):
    """Test Operations decision card action execution."""
    card_id = 'card-101'
    response = client.post('/api/v1/operations/action', json={
        'card_id': card_id,
        'action': 'APPROVE_RATE_CON',
        'comments': 'Approved by Mike'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert data['new_work_item_state'] == 'MIKE_APPROVED'

def test_stakeholder_data_isolation_and_roles(client):
    """Test External Stakeholder API excludes internal proprietary keys/scoring and handles roles."""
    for role in ["Broker", "Shipper", "Customer"]:
        response = client.get(f'/api/v1/stakeholder/shipment/L1T-2026-8804?role={role}')
        assert response.status_code == 200
        data = response.get_json()
        assert data["load_number"] == "L1T-2026-8804"
        assert data["role"] == role
        assert 'work_item_id' not in data
        assert 'cognitive_status' not in data

    # Customer view should exclude invoice packet status and broker reference
    res_cust = client.get('/api/v1/stakeholder/shipment/L1T-2026-8804?role=Customer')
    data_cust = res_cust.get_json()
    assert "invoice_packet_status" not in data_cust
    assert "broker_reference" not in data_cust
