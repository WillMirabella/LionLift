import pytest

import db

# Tests for GET /api/users/all-locations, the points the map shows.

URL = "/api/users/all-locations"


def test_returns_a_list_of_points(client, monkeypatch):
    monkeypatch.setattr(db, "get_users_locations", lambda: [(40.1, -75.1), (39.95, -75.16)])
    response = client.get(URL)
    assert response.status_code == 200 and response.is_json
    assert response.get_json() == [[40.1, -75.1], [39.95, -75.16]]


def test_empty_when_nobody_has_a_location(client, monkeypatch):
    monkeypatch.setattr(db, "get_users_locations", lambda: [])
    assert client.get(URL).get_json() == []


@pytest.mark.parametrize("method", ["post", "put", "delete"])
def test_read_only(client, method):
    assert getattr(client, method)(URL).status_code == 405


@pytest.mark.db
def test_points_come_from_saved_users(client, save_user):
    save_user("a@psu.edu", latitude=40.1, longitude=-75.1)
    points = client.get(URL).get_json()
    assert len(points) == 1
    lat, lng = points[0]
    assert abs(lat - 40.1) <= 0.015 + 1e-9 and abs(lng + 75.1) <= 0.015 + 1e-9


# The response only has points: no names, emails or ids
@pytest.mark.db
def test_no_personal_details(client, save_user):
    save_user("a@psu.edu", latitude=40.1, longitude=-75.1)
    for point in client.get(URL).get_json():
        assert isinstance(point, list) and len(point) == 2
        assert all(isinstance(value, float) for value in point)


# Known gap: every user's area is visible to anyone, signed in or not
@pytest.mark.xfail(reason="all-locations doesn't require a login token")
def test_locations_need_sign_in(client, monkeypatch):
    monkeypatch.setattr(db, "get_users_locations", lambda: [(40.1, -75.1)])
    assert client.get(URL).status_code == 401
