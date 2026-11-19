import math
import random

import pytest

# Tests for user_search.py (issues #22, #23). Skipped until that branch is merged.
user_search = pytest.importorskip("user_search")

from user_search import (  # noqa: E402
    USER_COLUMNS, approximate_location, check_location, distance_miles, filter_users, parse_sort,
    row_to_user, search_users, sort_users, user_location,
)

ABINGTON = (40.1157, -75.1135)
PHILLY = (39.9526, -75.1652)
NYC = (40.7128, -74.0060)
EARTH_HALF_CIRCUMFERENCE = math.pi * 3958.8


def make_user(id, first, last, gender=None, grad_year=None, major=None, payment=None, car_id=None, location=None):
    user = {column: None for column in USER_COLUMNS}
    user.update(id=id, first_name=first, last_name=last, gender=gender, grad_year=grad_year,
                major=major, preferred_payment=payment, car_id=car_id)
    if location is not None:
        user["latitude"], user["longitude"] = location
    return user


USERS = [
    make_user(1, "John", "Doe", "male", 2028, "Computer Science", "Cash", 1, PHILLY),
    make_user(2, "Bob", "Smith", "Male", 2027, "Biology", "Venmo", None, NYC),
    make_user(3, "Alice", "Jones", "female", 2028, "computer science", "venmo", 2, ABINGTON),
    make_user(4, "Dana", "Lee"),
    make_user(5, "erin", "adams", "female", 2026, "Nursing", "Zelle", None, (40.2, -75.1)),
]


def ids(users):
    return [user["id"] for user in users]


# ---- rows and locations ----

def test_row_to_user():
    user = row_to_user(tuple(range(len(USER_COLUMNS))))
    assert user["id"] == 0 and user["car_id"] == len(USER_COLUMNS) - 1


def test_row_to_user_wrong_length():
    with pytest.raises(ValueError):
        row_to_user((1, 2, 3))


def test_check_location():
    assert check_location(40, -75) == (40.0, -75.0)


@pytest.mark.parametrize("location", [(91, 0), (0, 181), (float("nan"), 0), (0, float("inf")), ("40", 0), (True, 0)])
def test_check_location_rejects(location):
    with pytest.raises(ValueError):
        check_location(*location)


@pytest.mark.parametrize("user, expected", [
    (USERS[0], PHILLY), (USERS[3], None), ({"latitude": 200, "longitude": 0}, None), ({"latitude": 40}, None),
])
def test_user_location(user, expected):
    assert user_location(user) == expected


# ---- distance ----

def test_distance_same_point():
    assert distance_miles(ABINGTON, ABINGTON) == 0.0


# Philadelphia to New York is about 81 miles in a straight line
def test_distance_known_value():
    assert distance_miles(PHILLY, NYC) == pytest.approx(80.6, abs=1.0)


def test_distance_one_degree_latitude():
    assert distance_miles((0, 0), (1, 0)) == pytest.approx(69.09, abs=0.05)


def test_distance_antipodes():
    assert distance_miles((0, 0), (0, 180)) == pytest.approx(EARTH_HALF_CIRCUMFERENCE)
    assert distance_miles((90, 0), (-90, 0)) == pytest.approx(EARTH_HALF_CIRCUMFERENCE)


def test_distance_across_date_line():
    assert distance_miles((0, 179.5), (0, -179.5)) == pytest.approx(69.09, abs=0.05)


def test_distance_symmetric():
    rng = random.Random(22)
    for _ in range(500):
        a = (rng.uniform(-90, 90), rng.uniform(-180, 180))
        b = (rng.uniform(-90, 90), rng.uniform(-180, 180))
        assert distance_miles(a, b) == pytest.approx(distance_miles(b, a))


# ---- filter_users ----

@pytest.mark.parametrize("filters, expected", [
    ({}, [1, 2, 3, 4, 5]),
    ({"genders": "MALE"}, [1, 2]),
    ({"genders": ["female", " Male "]}, [1, 2, 3, 5]),
    ({"majors": "Computer  Science"}, [1, 3]),
    ({"payments": ["venmo", "zelle"]}, [2, 3, 5]),
    ({"genders": [], "majors": "", "name": "  "}, [1, 2, 3, 4, 5]),
    ({"grad_years": 2028}, [1, 3]),
    ({"grad_years": [2026, 2027]}, [2, 5]),
    ({"grad_year_min": 2027}, [1, 2, 3]),
    ({"grad_year_max": 2027}, [2, 5]),
    ({"grad_year_min": 2027, "grad_year_max": 2027}, [2]),
    ({"role": "driver"}, [1, 3]),
    ({"role": "Rider"}, [2, 4, 5]),
    ({"name": "jo"}, [1, 3]),
    ({"name": "ERIN ADA"}, [5]),
    ({"name": "zzz"}, []),
    ({"exclude_ids": [1, 3]}, [2, 4, 5]),
    ({"origin": ABINGTON, "max_distance": 15}, [1, 3, 5]),
    ({"origin": ABINGTON, "max_distance": 0}, [3]),
    ({"genders": "female", "role": "rider", "grad_year_max": 2026}, [5]),
])
def test_filter_users(filters, expected):
    assert ids(filter_users(USERS, **filters)) == expected


# A user with no value for a field never matches a filter on it
def test_missing_values_dont_match():
    assert 4 not in ids(filter_users(USERS, genders="male"))
    assert 4 not in ids(filter_users(USERS, grad_year_max=3000))


@pytest.mark.parametrize("filters", [
    {"grad_year_min": 2029, "grad_year_max": 2027}, {"grad_year_min": "2027"}, {"grad_years": [2027.5]},
    {"grad_year_max": True}, {"role": "pilot"}, {"max_distance": 10},
    {"origin": ABINGTON, "max_distance": -1}, {"origin": (100, 0), "max_distance": 10},
])
def test_filter_users_rejects(filters):
    with pytest.raises(ValueError):
        filter_users(USERS, **filters)


def test_filter_does_not_change_input():
    before = [dict(user) for user in USERS]
    filter_users(USERS, genders="male", origin=ABINGTON, max_distance=100)
    assert USERS == before


# ---- parse_sort ----

@pytest.mark.parametrize("text, expected", [
    ("distance", [("distance", False)]),
    ("-grad_year, last_name", [("grad_year", True), ("last_name", False)]),
    ("+Major", [("major", False)]),
    (None, []), ("", []), (" , ,", []),
])
def test_parse_sort(text, expected):
    assert parse_sort(text) == expected


@pytest.mark.parametrize("text", ["age", "distance,-distance", "-", "phone"])
def test_parse_sort_rejects(text):
    with pytest.raises(ValueError):
        parse_sort(text)


# ---- sort_users ----

@pytest.mark.parametrize("order, expected", [
    ([], [5, 1, 3, 4, 2]),
    ([("distance", False)], [3, 5, 1, 2, 4]),
    ([("distance", True)], [2, 1, 5, 3, 4]),
    ([("grad_year", True), ("first_name", False)], [3, 1, 2, 5, 4]),
    ([("first_name", False)], [3, 2, 4, 5, 1]),
])
def test_sort_users(order, expected):
    assert ids(sort_users(USERS, order, ABINGTON)) == expected


# Users missing the sort value stay last in both directions
@pytest.mark.parametrize("descending", [False, True])
def test_missing_values_last(descending):
    assert ids(sort_users(USERS, [("grad_year", descending)]))[-1] == 4


def test_sort_distance_needs_origin():
    with pytest.raises(ValueError):
        sort_users(USERS, [("distance", False)])


def test_ties_are_stable():
    twins = [make_user(9, "Sam", "Kim", grad_year=2027), make_user(8, "Sam", "Kim", grad_year=2027)]
    assert ids(sort_users(twins, [("grad_year", False)])) == [8, 9]
    assert ids(sort_users(list(reversed(twins)), [("grad_year", True)])) == [8, 9]


def test_input_order_doesnt_matter():
    rng = random.Random(23)
    order = [("major", False), ("distance", True)]
    expected = ids(sort_users(USERS, order, ABINGTON))
    for _ in range(50):
        shuffled = list(USERS)
        rng.shuffle(shuffled)
        assert ids(sort_users(shuffled, order, ABINGTON)) == expected


# ---- search_users ----

def test_search_filters_sorts_and_adds_distance():
    result = search_users(USERS, {"role": "driver"}, [("distance", True)], ABINGTON)
    assert ids(result) == [1, 3]
    assert result[0]["distance"] == pytest.approx(distance_miles(ABINGTON, PHILLY), abs=0.01)
    assert result[1]["distance"] == 0.0


def test_search_without_origin_has_no_distance():
    assert "distance" not in search_users(USERS)[0]


def test_search_unknown_location_is_none():
    result = search_users(USERS, {}, [], ABINGTON)
    assert next(user for user in result if user["id"] == 4)["distance"] is None


def test_search_returns_copies():
    result = search_users(USERS, {}, [], ABINGTON)
    result[0]["first_name"] = "changed"
    assert "distance" not in USERS[0] and USERS[0]["first_name"] != "changed"


def test_search_rejects_origin_in_filters():
    with pytest.raises(ValueError):
        search_users(USERS, {"origin": ABINGTON})


# ---- approximate_location ----

# Farthest a point can move: half the diagonal of a 1 mile square cell
MAX_MOVE_MILES = math.sqrt(0.5 ** 2 + 0.5 ** 2)


def test_approximate_moves_less_than_a_mile():
    rng = random.Random(7)
    for _ in range(5000):
        point = (rng.uniform(-80, 80), rng.uniform(-179, 179))
        assert distance_miles(point, approximate_location(point)) <= MAX_MOVE_MILES + 1e-6


def test_approximate_is_stable():
    rng = random.Random(8)
    for _ in range(2000):
        once = approximate_location((rng.uniform(-80, 80), rng.uniform(-179, 179)))
        assert approximate_location(once) == once


def test_nearby_points_share_a_cell():
    center = approximate_location(ABINGTON)
    # Points a few hundred feet from the cell center land in the same cell
    for d_lat, d_lon in [(0.001, 0), (-0.001, 0), (0, 0.001), (0, -0.001)]:
        assert approximate_location((center[0] + d_lat, center[1] + d_lon)) == center


def test_far_points_differ():
    assert approximate_location(ABINGTON) != approximate_location(PHILLY)


def test_bigger_cells_move_points_further():
    rng = random.Random(9)
    for _ in range(500):
        point = (rng.uniform(-60, 60), rng.uniform(-170, 170))
        assert distance_miles(point, approximate_location(point, cell_miles=5)) <= 5 * MAX_MOVE_MILES + 1e-6


@pytest.mark.parametrize("point, cell", [((91, 0), 1), ((0, 181), 1), (("x", 0), 1), ((40, -75), 0), ((40, -75), -1)])
def test_approximate_rejects(point, cell):
    with pytest.raises(ValueError):
        approximate_location(point, cell_miles=cell)


def test_near_poles_stay_valid():
    for point in [(89.999, 10), (-89.999, -170), (0, 179.999), (0, -179.999)]:
        lat, lon = approximate_location(point)
        assert -90 <= lat <= 90 and -180 <= lon <= 180
