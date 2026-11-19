import re

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

from schedule_similarity import (
    DEFAULT_CUTOFF_HOURS, DEFAULT_GRACE_HOURS, parse_schedule, schedule_similarity, time_closeness, to_hours,
)
from services.verification import check_code, hash_code, is_psu_email, make_code, normalize_email

# Property tests: instead of a few hand-picked examples, Hypothesis generates
# hundreds of inputs and checks that a rule holds for every one of them. When a
# rule breaks, it shrinks the input down to the smallest case that fails.

# ---- strategies ----

# A time of day in hours, kept on a quarter-minute grid so sums stay exact enough
times = st.integers(min_value=0, max_value=24 * 60 * 4).map(lambda q: q / 240)


# A valid (start, end) pair with start before end
@st.composite
def blocks(draw):
    start = draw(st.integers(min_value=0, max_value=24 * 60 - 1))
    end = draw(st.integers(min_value=start + 1, max_value=24 * 60))
    return (start / 60, end / 60)


# A five-day schedule where each day is a block or None
schedules = st.lists(st.one_of(st.none(), blocks()), min_size=5, max_size=5)


# A schedule with at least one day on campus
busy_schedules = schedules.filter(lambda s: any(day is not None for day in s))


# ---- time_closeness ----

@given(st.floats(min_value=0, max_value=48, allow_nan=False))
def test_closeness_is_between_0_and_1(gap):
    assert 0.0 <= time_closeness(gap) <= 1.0


@given(st.floats(min_value=0, max_value=48, allow_nan=False), st.floats(min_value=0, max_value=48, allow_nan=False))
def test_closeness_never_rises_as_gap_grows(a, b):
    small, large = sorted((a, b))
    assert time_closeness(small) >= time_closeness(large)


# f is continuous: tiny changes in the gap give tiny changes in the score
@given(st.floats(min_value=0, max_value=3, allow_nan=False))
def test_closeness_is_continuous(gap):
    step = 1e-6
    slope = 1 / (DEFAULT_CUTOFF_HOURS - DEFAULT_GRACE_HOURS)
    assert abs(time_closeness(gap + step) - time_closeness(gap)) <= slope * step + 1e-9


# ---- schedule_similarity ----

@given(schedules, schedules)
def test_score_is_between_0_and_100(a, b):
    assert 0.0 <= schedule_similarity(a, b) <= 100.0


@given(schedules, schedules)
def test_score_is_symmetric(a, b):
    assert schedule_similarity(a, b) == pytest.approx(schedule_similarity(b, a))


@given(busy_schedules)
def test_same_schedule_scores_100(a):
    assert schedule_similarity(a, a) == pytest.approx(100.0)


# Moving both people by the same amount doesn't change how well they match
@given(schedules, schedules, st.integers(min_value=-120, max_value=120))
def test_score_ignores_shifting_both(a, b, minutes):
    shift = minutes / 60

    def moved(schedule):
        return [None if day is None else (day[0] + shift, day[1] + shift) for day in schedule]

    every_time = [t for s in (a, b) for day in s if day for t in day]
    assume(all(0 <= t + shift <= 24 for t in every_time))
    assert schedule_similarity(moved(a), moved(b)) == pytest.approx(schedule_similarity(a, b))


# Moving one person's arrival further from the other's never helps
@given(blocks(), blocks(), st.integers(min_value=1, max_value=180))
def test_moving_apart_never_raises_score(a, b, minutes):
    gap = abs(a[0] - b[0])
    direction = 1 if a[0] >= b[0] else -1
    new_start = a[0] + direction * minutes / 60
    assume(0 <= new_start and a[1] - new_start > 1e-6)
    before = schedule_similarity([a] + [None] * 4, [b] + [None] * 4)
    after = schedule_similarity([(new_start, a[1])] + [None] * 4, [b] + [None] * 4)
    assert abs(new_start - b[0]) > gap
    assert after <= before + 1e-9


# The score is the average of the day scores, so adding a day where neither
# person is on campus changes nothing
@given(schedules, schedules)
def test_shared_days_off_dont_count(a, b):
    assume(len(a) == 5)
    assert schedule_similarity(a + [None, None], b + [None, None]) == pytest.approx(schedule_similarity(a, b))


# ---- reading times and schedules ----

@given(st.integers(min_value=0, max_value=23), st.integers(min_value=0, max_value=59))
def test_24_hour_text(hour, minute):
    assert to_hours(f"{hour}:{minute:02d}") == pytest.approx(hour + minute / 60)


@given(st.integers(min_value=1, max_value=12), st.integers(min_value=0, max_value=59), st.sampled_from(["AM", "PM", "am", "pm", "a.m.", "p.m."]))
def test_12_hour_text(hour, minute, meridiem):
    expected = (hour % 12) + (12 if meridiem.lower().startswith("p") else 0) + minute / 60
    assert to_hours(f"{hour}:{minute:02d} {meridiem}") == pytest.approx(expected)


# Writing a schedule the way Postgres does and reading it back gives the same days
@given(schedules)
def test_database_text_round_trip(schedule):
    parts = ["NULL" if day is None else f'"({day[0]!r},{day[1]!r})"' for day in schedule]
    text = "{" + ",".join(parts) + "}"
    assert parse_schedule(text) == [None if day is None else (pytest.approx(day[0]), pytest.approx(day[1])) for day in schedule]


# ---- email and codes ----

@given(st.text(max_size=40))
def test_normalize_is_idempotent(text):
    once = normalize_email(text)
    assert normalize_email(once) == once


@given(st.from_regex(r"[a-z]{1,3}[0-9]{1,4}", fullmatch=True))
def test_psu_ids_are_accepted_in_any_case(local):
    assert is_psu_email(normalize_email(f"  {local.upper()}@PSU.EDU "))


@given(st.text(max_size=30))
def test_accepted_emails_end_in_psu_edu(text):
    if is_psu_email(text):
        assert text.endswith("@psu.edu")


@given(st.integers(min_value=0, max_value=200))
def test_codes_are_six_digits_and_check_out(_):
    code, code_hash = make_code()
    assert re.fullmatch(r"\d{6}", code)
    assert code_hash == hash_code(code)
    assert check_code(code, code_hash)


@given(st.from_regex(r"\d{6}", fullmatch=True), st.from_regex(r"\d{6}", fullmatch=True))
def test_wrong_code_never_checks_out(a, b):
    assume(a != b)
    assert not check_code(b, hash_code(a))
