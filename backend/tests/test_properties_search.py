import math

import pytest
from hypothesis import given
from hypothesis import strategies as st

# Property tests for user_search.py distances (issues #22, #23).
# Skipped until that branch is merged.
user_search = pytest.importorskip("user_search")

points = st.tuples(st.floats(min_value=-89, max_value=89), st.floats(min_value=-179, max_value=179))


@given(points, points)
def test_distance_is_symmetric_and_bounded(a, b):
    d = user_search.distance_miles(a, b)
    assert d == pytest.approx(user_search.distance_miles(b, a), abs=1e-6)
    assert 0 <= d <= math.pi * user_search.EARTH_RADIUS_MILES + 1e-6


@given(points)
def test_distance_to_itself_is_zero(a):
    assert user_search.distance_miles(a, a) == pytest.approx(0.0, abs=1e-9)


@given(points, points, points)
def test_distance_triangle_inequality(a, b, c):
    d = user_search.distance_miles
    assert d(a, c) <= d(a, b) + d(b, c) + 1e-6


# Sorting only reorders: the same users come back, none added or lost
@given(st.lists(st.tuples(st.integers(2020, 2032), st.sampled_from(["Lee", "adams", "Smith", "doe"])), max_size=30),
       st.sampled_from(["grad_year", "-grad_year", "last_name", "-last_name,grad_year"]))
def test_sort_is_a_reordering(rows, sort):
    users = [{"id": i, "grad_year": year, "last_name": name, "first_name": "x", "major": None}
             for i, (year, name) in enumerate(rows)]
    result = user_search.sort_users(users, user_search.parse_sort(sort))
    assert sorted(u["id"] for u in result) == list(range(len(users)))


# Filtering only removes: every result was in the input and matches the filter
@given(st.lists(st.sampled_from(["Biology", "biology", "Nursing", None]), max_size=30))
def test_filter_returns_matching_subset(majors):
    users = [{"id": i, "major": m, "gender": None, "preferred_payment": None, "grad_year": None,
              "car_id": None, "first_name": "x", "last_name": "y"} for i, m in enumerate(majors)]
    result = user_search.filter_users(users, majors=["biology"])
    assert {u["id"] for u in result} == {i for i, m in enumerate(majors) if m and m.lower() == "biology"}
