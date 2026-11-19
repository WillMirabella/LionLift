import pytest

import db

# Tests for GET /api/users/, browsing with filters and sorting (issues #22, #23).
# Skipped until that branch, which adds user_search.py, is merged.
pytest.importorskip("user_search")

URL = "/api/users/"


# Serves the sample rows instead of reading the database
@pytest.fixture
def users(monkeypatch, sample_rows):
    monkeypatch.setattr(db, "get_all_users", lambda: sample_rows)
    return sample_rows


def get_ids(client, query=""):
    response = client.get(URL + query)
    assert response.status_code == 200, response.get_json()
    return [user["id"] for user in response.get_json()]


def test_lists_all_users(client, users):
    assert sorted(get_ids(client)) == [1, 2, 3, 4, 5]


def test_hides_phone_and_email(client, users):
    for user in client.get(URL).get_json():
        assert "phone" not in user and "email" not in user


# The password hash and the parts of the address that pin down a home are
# never sent; city and state are fine to show
def test_hides_password_and_home_address(client, users):
    for user in client.get(URL).get_json():
        assert not {"password", "street", "zip"} & set(user)
        assert user["city"] == "Abington" and user["state"] == "PA"


# Coordinates are stored as text, and still count for distance
def test_text_coordinates_are_used(client, monkeypatch, make_row):
    rows = [make_row(1, latitude="40.1175", longitude="-75.1091"), make_row(2, latitude="not a number", longitude="1")]
    monkeypatch.setattr(db, "get_all_users", lambda: rows)
    data = client.get(URL + "?lat=40.1175&lon=-75.1091&sort=distance").get_json()
    assert data[0]["id"] == 1 and data[0]["distance"] < 1
    assert data[1]["id"] == 2 and data[1]["distance"] is None


# With no sort given, results come back by last name: adams, Doe, Jones, Lee, Smith
@pytest.mark.parametrize("query, expected", [
    ("?gender=female", [5, 3]),
    ("?gender=male&gender=female", [5, 1, 3, 2]),
    ("?gender=male,female", [5, 1, 3, 2]),
    ("?major=computer%20science", [1, 3]),
    ("?payment=venmo", [3, 2]),
    ("?grad_year=2026,2027", [5, 2]),
    ("?grad_year_min=2027&grad_year_max=2027", [2]),
    ("?role=driver", [1, 3]),
    ("?role=rider&sort=-grad_year", [2, 5, 4]),
    ("?name=jo", [1, 3]),
    ("?exclude=1,2", [5, 3, 4]),
    ("?sort=first_name", [3, 2, 4, 5, 1]),
    ("?sort=-grad_year,last_name", [1, 3, 2, 5, 4]),
])
def test_filters_and_sorting(client, users, query, expected):
    assert get_ids(client, query) == expected


def test_distance_field_with_origin(client, users):
    data = client.get(URL + "?lat=40.1&lon=-75.1").get_json()
    assert all("distance" in user for user in data)


@pytest.mark.parametrize("query", [
    "?sort=age", "?grad_year_min=abc", "?grad_year=2027,x", "?lat=40", "?lon=-75",
    "?max_distance=5", "?max_distance=far&lat=40&lon=-75", "?role=pilot", "?lat=100&lon=0",
    "?grad_year_min=2029&grad_year_max=2027", "?sort=distance",
])
def test_bad_input_is_400_with_reason(client, users, query):
    response = client.get(URL + query)
    assert response.status_code == 400
    assert response.get_json()["error"]


def test_no_trailing_slash_redirects(client, users):
    response = client.get("/api/users")
    assert response.status_code in (301, 308)
    assert response.headers["Location"].endswith("/api/users/")


# A problem with the stored data is the server's fault, not the request's
def test_schema_change_is_500(client, monkeypatch, sample_rows):
    monkeypatch.setattr(db, "get_all_users", lambda: [row + ("extra",) for row in sample_rows])
    # Testing mode re-raises errors; turn that off to see the real response
    monkeypatch.setitem(client.application.config, "PROPAGATE_EXCEPTIONS", False)
    assert client.get(URL).status_code == 500


# Against the real test database
@pytest.mark.db
def test_reads_from_database(client, save_user):
    for email, year in (("a@psu.edu", 2027), ("b@psu.edu", 2028)):
        save_user(email, grad_year=year, schedule=[(9, 17)] * 5)
    data = client.get(URL + "?sort=-grad_year").get_json()
    assert [user["grad_year"] for user in data] == [2028, 2027]
