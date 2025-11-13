import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    # Keep a deep copy of the original activities and restore after each test
    original = copy.deepcopy(activities)
    try:
        yield
    finally:
        activities.clear()
        activities.update(original)


def test_get_activities_returns_activities():
    client = TestClient(app)
    res = client.get("/activities")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, dict)
    # A known activity exists in the sample data
    assert "Chess Club" in data


def test_signup_and_duplicate_rejection():
    client = TestClient(app)
    activity = "Chess Club"
    email = "testuser@example.com"

    # Sign up should succeed
    res = client.post(f"/activities/{quote(activity)}/signup", params={"email": email})
    assert res.status_code == 200
    body = res.json()
    assert "Signed up" in body.get("message", "")

    # Signing up same email again should return 400
    res2 = client.post(f"/activities/{quote(activity)}/signup", params={"email": email})
    assert res2.status_code == 400
    body2 = res2.json()
    assert "already signed up" in body2.get("detail", "")


def test_unregister_participant_and_failure():
    client = TestClient(app)
    activity = "Chess Club"
    # choose an existing participant from the seeded data
    existing = activities[activity]["participants"][0]

    # Unregister should succeed
    res = client.delete(f"/activities/{quote(activity)}/unregister", params={"email": existing})
    assert res.status_code == 200
    body = res.json()
    assert "Unregistered" in body.get("message", "")

    # Trying to unregister same email again should fail with 400
    res2 = client.delete(f"/activities/{quote(activity)}/unregister", params={"email": existing})
    assert res2.status_code == 400
    body2 = res2.json()
    assert "not signed up" in body2.get("detail", "")
