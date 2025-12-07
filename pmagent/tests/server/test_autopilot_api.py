"""
Tests for Autopilot Backend API (Phase C).
"""

from unittest.mock import patch

from fastapi.testclient import TestClient

from pmagent.server.autopilot_api import app

client = TestClient(app)


def test_health_check():
    """Verify health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "phase": "C"}


def test_intent_handling_dry_run_default():
    """Verify intent handling returns planned status when dry_run is True (default)."""
    payload = {"intent_text": "status", "context": {"caller": "test_suite"}}
    response = client.post("/autopilot/intent", json=payload)

    assert response.status_code == 200
    data = response.json()

    # Default behavior: accepted=False, status="planned" (dry_run defaults to True)
    assert data["accepted"] is False
    assert data["status"] == "planned"
    assert "plan_id" in data
    assert data["plan_id"].startswith("autopilot-plan-")
    assert "Dry run" in data["summary"]


def test_intent_handling_dry_run_explicit():
    """Verify intent handling returns planned status when dry_run is explicitly True."""
    payload = {"intent_text": "status", "context": {"dry_run": True}}
    response = client.post("/autopilot/intent", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["accepted"] is False
    assert data["status"] == "planned"


def test_intent_validation():
    """Verify validation of intent payload."""
    # Missing intent_text
    response = client.post("/autopilot/intent", json={"context": {}})
    assert response.status_code == 422


def test_intent_execution_valid_status():
    """Verify that valid 'status' intent executes when dry_run is False."""
    payload = {"intent_text": "status", "context": {"dry_run": False}}

    with patch("pmagent.server.autopilot_api.subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "System status: OK"
        mock_run.return_value.stderr = ""

        response = client.post("/autopilot/intent", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["accepted"] is True
        assert data["status"] == "completed"
        assert "Command executed" in data["summary"]
        mock_run.assert_called_once()


def test_intent_execution_unknown_intent():
    """Verify that unknown intents are rejected with 400 error."""
    payload = {"intent_text": "unknown_command", "context": {"dry_run": False}}

    response = client.post("/autopilot/intent", json=payload)

    assert response.status_code == 400
    assert "Unknown intent" in response.json()["detail"]


def test_intent_execution_valid_health():
    """Verify that valid 'health' intent executes when dry_run is False."""
    payload = {"intent_text": "health", "context": {"dry_run": False}}

    with patch("pmagent.server.autopilot_api.subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "Health: OK"
        mock_run.return_value.stderr = ""

        response = client.post("/autopilot/intent", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["accepted"] is True
        assert data["status"] == "completed"
        mock_run.assert_called_once()


def test_intent_execution_command_failure():
    """Verify that command failures are reported correctly."""
    payload = {"intent_text": "status", "context": {"dry_run": False}}

    with patch("pmagent.server.autopilot_api.subprocess.run") as mock_run:
        mock_run.return_value.returncode = 1
        mock_run.return_value.stdout = ""
        mock_run.return_value.stderr = "Command failed"

        response = client.post("/autopilot/intent", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["accepted"] is True
        assert data["status"] == "failed"
