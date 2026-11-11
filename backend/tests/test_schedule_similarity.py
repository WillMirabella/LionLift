import math
import random
from datetime import time

import pytest

from schedule_similarity import (
    day_scores, day_similarity, parse_day, parse_schedule, schedule_similarity,
    time_closeness, to_hours,
)

# Tests for schedule_similarity.py (issue #45)

FULL_WEEK = [(9, 17)] * 5
NO_DAYS = [None] * 5


# ---- to_hours ----

@pytest.mark.parametrize("value, expected", [
    (9, 9.0), (9.5, 9.5), (0, 0.0), (24, 24.0),
    (time(9, 30), 9.5),
    ("9", 9.0), ("09:30", 9.5), ("17:45", 17.75), ("24:00", 24.0), (" 9.5 ", 9.5),
    ("9:30 AM", 9.5), ("2:15pm", 14.25), ("9 a.m.", 9.0), ("12:00 PM", 12.0), ("12:30 AM", 0.5),
])
def test_to_hours_accepts(value, expected):
    assert to_hours(value) == pytest.approx(expected)


def test_to_hours_seconds_from_time_object():
    assert to_hours(time(9, 0, 36)) == pytest.approx(9.01)


@pytest.mark.parametrize("value", [
    -1, 24.01, 25, "25:00", "24:30", "-1",
    float("nan"), float("inf"), "nan", "inf",
    "", "abc", "9:75", "13 PM", "0 AM", "9:30 m", "9:3", "9::30",
    True, False, None, [9], {"h": 9},
])
def test_to_hours_rejects(value):
    with pytest.raises(ValueError):
        to_hours(value)


# Known bug: text that looks like a decimal is read as decimal hours
@pytest.mark.xfail(reason="'9.30' is read as 9.3 hours (9:18), not 9:30")
def test_to_hours_dot_separated_minutes():
    assert to_hours("9.30") == 9.5


# ---- parse_day ----

@pytest.mark.parametrize("day", [None, (), [], (None, None), [None, None], "", "NULL", "null", [None, (), None]])
def test_parse_day_empty(day):
    assert parse_day(day) is None


@pytest.mark.parametrize("day, expected", [
    ((9, 17), (9.0, 17.0)),
    (["9:00", "5:00 PM"], (9.0, 17.0)),
    ([(14, 16), (9, 11)], (9.0, 16.0)),
    ([(9, 11), None, (13, 15)], (9.0, 15.0)),
    ([(9, 12), (10, 11)], (9.0, 12.0)),
    ('"(9,17)"', (9.0, 17.0)),
    ("(9.5,15.25)", (9.5, 15.25)),
    ("{9,17}", (9.0, 17.0)),
])
def test_parse_day_valid(day, expected):
    assert parse_day(day) == expected


@pytest.mark.parametrize("day", [
    (9, None), (None, 17), "(9,)", [(9, 11), (13, None)],
    (17, 9), (9, 9), ("9:00", "9:00"), [(9, 11), (15, 14)],
    (9,), (9, 12, 17), 9, {"start": 9}, "9-17", "(9,17",
])
def test_parse_day_invalid(day):
    with pytest.raises(ValueError):
        parse_day(day)


# ---- parse_schedule ----

def test_parse_schedule_missing_is_no_days():
    assert parse_schedule(None) == NO_DAYS


def test_parse_schedule_pads_short_lists():
    assert parse_schedule([(9, 17)]) == [(9.0, 17.0)] + [None] * 4
    assert parse_schedule([]) == NO_DAYS


def test_parse_schedule_allows_weekends():
    assert len(parse_schedule([(9, 17)] * 7)) == 7


@pytest.mark.parametrize("text, expected", [
    ('{"(9,17)",NULL,"(9.5,15.25)",NULL,"(8,12)"}', [(9.0, 17.0), None, (9.5, 15.25), None, (8.0, 12.0)]),
    ("{NULL,NULL,NULL,NULL,NULL}", NO_DAYS),
    ("{{9,17},{9,17},{9,17},{9,17},{9,17}}", [(9.0, 17.0)] * 5),
    ("{}", NO_DAYS),
])
def test_parse_schedule_database_text(text, expected):
    assert parse_schedule(text) == expected


@pytest.mark.parametrize("schedule", [
    [(9, 17)] * 8, "9,17", '{"(9,17)', "{{9,17}", '{"(9,17),NULL}', 5, {"monday": (9, 17)},
])
def test_parse_schedule_invalid(schedule):
    with pytest.raises(ValueError):
        parse_schedule(schedule)


# Known bugs: text times saved through psycopg2 don't read back
@pytest.mark.xfail(reason="escaped quotes from text times aren't handled by the database text parser")
def test_parse_schedule_database_text_with_string_times():
    assert parse_schedule('{"(\\"9:30 AM\\",\\"5:00 PM\\")",NULL}') == [(9.5, 17.0)] + [None] * 4


@pytest.mark.xfail(reason="HH:MM:SS from datetime.time values isn't accepted")
def test_parse_schedule_database_text_with_time_objects():
    assert parse_schedule('{"(09:30:00,17:00:00)",NULL}') == [(9.5, 17.0)] + [None] * 4


# ---- time_closeness ----

@pytest.mark.parametrize("gap, expected", [
    (0, 1.0), (0.25, 1.0), (1.125, 0.5), (2.0, 0.0), (10.0, 0.0),
])
def test_time_closeness_defaults(gap, expected):
    assert time_closeness(gap) == pytest.approx(expected)


# 9.1 - 8.85 is slightly more than 0.25 in floating point
def test_time_closeness_floating_point_edge():
    assert time_closeness(abs(9.1 - 8.85)) == 1.0


def test_time_closeness_zero_grace():
    assert time_closeness(0, grace=0, cutoff=1) == 1.0
    assert time_closeness(0.5, grace=0, cutoff=1) == pytest.approx(0.5)


def test_time_closeness_negative_gap():
    with pytest.raises(ValueError):
        time_closeness(-0.5)


# ---- day_similarity ----

def test_day_neither_on_campus_is_skipped():
    assert day_similarity(None, None) is None


def test_day_only_one_on_campus_is_zero():
    assert day_similarity((9, 17), None) == 0.0
    assert day_similarity(None, (9, 17)) == 0.0


def test_day_one_shared_leg_is_half():
    assert day_similarity((9, 11), (9, 17)) == 0.5
    assert day_similarity((8, 17), (13, 17)) == 0.5


# ---- schedule_similarity ----

def test_identical_schedules():
    assert schedule_similarity(FULL_WEEK, FULL_WEEK) == 100.0


def test_no_shared_days():
    a = [(9, 17), None, (9, 17), None, None]
    b = [None, (9, 17), None, (9, 17), None]
    assert schedule_similarity(a, b) == 0.0


# Never overlap, but arrivals and departures are each 1.25 h apart
def test_close_but_not_overlapping():
    assert schedule_similarity([(9, 10)] * 5, [(10.25, 11.25)] * 5) == pytest.approx(100 * 0.75 / 1.75)


# Overlap 5 hours, but arrivals and departures are each 2 h apart
def test_overlapping_but_far_apart():
    assert schedule_similarity([(8, 17)] * 5, [(10, 15)] * 5) == 0.0


def test_days_off_for_both_are_skipped():
    a = [(9, 17), None, None, None, None]
    assert schedule_similarity(a, list(a)) == 100.0


@pytest.mark.parametrize("a, b", [(NO_DAYS, NO_DAYS), (None, None), (None, FULL_WEEK)])
def test_nothing_to_match_on(a, b):
    assert schedule_similarity(a, b) == 0.0


# Monday 0.75, Tuesday 0 (only a), rest skipped: average 0.375
def test_known_value():
    a = [(9, 17), (9, 17), None, None, None]
    b = [(9, 18.125), None, None, None, None]
    assert schedule_similarity(a, b) == pytest.approx(37.5)


def test_input_formats_agree():
    other = [(9.5, 16), (9, 17), (10, 15), None, (8, 13)]
    expected = schedule_similarity([(9, 17), None, (9.5, 15.25), None, (8, 12)], other)
    as_strings = [("9:00", "5:00 PM"), None, ("09:30", "15:15"), None, ("8 am", "12 pm")]
    as_text = '{"(9,17)",NULL,"(9.5,15.25)",NULL,"(8,12)"}'
    assert schedule_similarity(as_strings, other) == pytest.approx(expected)
    assert schedule_similarity(as_text, other) == pytest.approx(expected)


def test_five_vs_seven_days():
    weekend = FULL_WEEK + [(10, 14), (10, 14)]
    assert schedule_similarity(FULL_WEEK, weekend) == pytest.approx(100 * 5 / 7)


def test_day_scores_breakdown():
    a = [(9, 17), (9, 17), None, None, None]
    b = [(9, 17), None, None, None, (9, 17)]
    assert day_scores(a, b) == [1.0, 0.0, None, None, 0.0]


def test_custom_tuning():
    a, b = [(9, 17)] * 5, [(10, 18)] * 5
    assert schedule_similarity(a, b) == pytest.approx(100 * (2.0 - 1) / 1.75)
    assert schedule_similarity(a, b, grace=1, cutoff=3) == 100.0


@pytest.mark.parametrize("grace, cutoff", [
    (2, 1), (1, 1), (-1, 2), (0, float("inf")), (float("nan"), 2), (True, 2), ("0", 2),
])
def test_bad_tuning(grace, cutoff):
    with pytest.raises(ValueError):
        schedule_similarity(FULL_WEEK, FULL_WEEK, grace=grace, cutoff=cutoff)


def test_bad_schedule_raises():
    with pytest.raises(ValueError):
        schedule_similarity([(17, 9)], FULL_WEEK)


def test_inputs_not_modified():
    a, b = [(9, 17), None], [(9, 17)]
    schedule_similarity(a, b)
    assert a == [(9, 17), None] and b == [(9, 17)]


# ---- properties over random schedules ----

def _random_schedule(rng):
    schedule = []
    for _ in range(5):
        if rng.random() < 0.3:
            schedule.append(None)
        else:
            start = rng.uniform(6, 18)
            schedule.append((start, rng.uniform(start + 0.5, 23)))
    return schedule


def test_bounded_and_symmetric():
    rng = random.Random(487)
    for _ in range(2000):
        a, b = _random_schedule(rng), _random_schedule(rng)
        score = schedule_similarity(a, b)
        assert 0.0 <= score <= 100.0
        assert math.isclose(score, schedule_similarity(b, a))


def test_self_similarity():
    rng = random.Random(3)
    for _ in range(500):
        a = _random_schedule(rng)
        if any(day is not None for day in a):
            assert schedule_similarity(a, a) == 100.0


def test_moving_apart_never_helps():
    previous = 100.0
    for step in range(13):
        shift = step * 0.25
        score = schedule_similarity(FULL_WEEK, [(9 + shift, 17 - shift / 2)] * 5)
        assert score <= previous + 1e-9
        previous = score
