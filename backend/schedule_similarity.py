import math
import re
from datetime import time as dt_time

# Compares two weekly schedules and returns how compatible they are for
# sharing rides, as a percentage from 0 to 100.
#
# A schedule is the same structure as User.schedule: one entry per weekday,
# index 0 = Monday through 4 = Friday. Each entry is None if the person is not
# on campus that day, or a (start_time, end_time) pair in hours.
#
# The score is based on how close the two people's arrival and departure
# times are, not on how much their time on campus overlaps. Overlap is a poor
# fit for carpooling: two people who arrive at the same time can share the
# morning ride even if one leaves hours before the other, and two schedules
# that overlap most of the day can still have arrivals far apart.
#
# For a day where both people are on campus:
#   dS = |start_a - start_b|, dE = |end_a - end_b|
#   day score = (f(dS) + f(dE)) / 2
# where f(d) is 1 when d <= grace, 0 when d >= cutoff, and falls linearly
# from 1 to 0 in between: f(d) = (cutoff - d) / (cutoff - grace).
#
# A day where only one person is on campus scores 0. A day where neither is
# on campus is skipped. The final score is the average day score over the
# days that were not skipped, times 100.

# Number of days in a normal schedule, and the most we accept (weekends)
DAYS_PER_WEEK = 5
MAX_DAYS = 7

# Default tuning values, in hours
DEFAULT_GRACE_HOURS = 0.25
DEFAULT_CUTOFF_HOURS = 2.0

# Small tolerance so floating point error doesn't change a result,
# e.g. 9.1 - 8.85 coming out as 0.2500000001 instead of 0.25
EPSILON = 1e-9

# Matches times like "9", "09:30", "9:30pm", "9:30 a.m."
TIME_PATTERN = re.compile(r"^(\d{1,2})(?::(\d{2}))?\s*([ap])?\.?\s*(m\.?)?$", re.IGNORECASE)


# Converts a single time value into hours as a float.
# Accepts numbers, datetime.time objects and strings like "9:30" or "2:15 PM".
def to_hours(value):
    # bool is a subclass of int, so True would otherwise be read as 1:00
    if isinstance(value, bool):
        raise ValueError(f"invalid time: {value!r}")

    if isinstance(value, (int, float)):
        hours = float(value)

    elif isinstance(value, dt_time):
        hours = value.hour + value.minute / 60 + value.second / 3600

    elif isinstance(value, str):
        hours = _parse_time_string(value)

    else:
        raise ValueError(f"invalid time: {value!r}")

    # NaN passes the range check below because comparisons with it are always false
    if not math.isfinite(hours):
        raise ValueError(f"invalid time: {value!r}")

    if hours < 0 or hours > 24:
        raise ValueError(f"time must be between 0 and 24 hours, got {value!r}")

    return hours


# Parses a time written as text into hours
def _parse_time_string(text):
    text = text.strip()

    # Plain decimal hours, like "9.5"
    try:
        return float(text)
    except ValueError:
        pass

    match = TIME_PATTERN.match(text)
    if not match:
        raise ValueError(f"invalid time: {text!r}")

    hour = int(match.group(1))
    minute = int(match.group(2) or 0)
    meridiem = match.group(3)

    # A lone "m" with no a or p, like "9:30 m", is not a valid time
    if match.group(4) and not meridiem:
        raise ValueError(f"invalid time: {text!r}")

    if minute > 59:
        raise ValueError(f"invalid time: {text!r}")

    if meridiem:
        # 12-hour clock: hours run 1 to 12, 12 AM is midnight, 12 PM is noon
        if hour < 1 or hour > 12:
            raise ValueError(f"invalid time: {text!r}")
        hour = hour % 12
        if meridiem.lower() == "p":
            hour += 12
    else:
        # 24-hour clock: 24:00 is allowed as end of day, nothing past it
        if hour > 24 or (hour == 24 and minute > 0):
            raise ValueError(f"invalid time: {text!r}")

    return hour + minute / 60


# Returns True if value looks like a single time rather than a pair or list
def _is_time_value(value):
    return isinstance(value, (int, float, str, dt_time)) and not isinstance(value, bool)


# Returns True if a day entry means the person is not on campus
def _is_empty_day(day):
    if day is None:
        return True
    if isinstance(day, str):
        return day.strip().upper() in ("", "NULL", "NONE")
    if isinstance(day, (list, tuple)):
        return len(day) == 0 or all(part is None for part in day)
    return False


# Converts one (start, end) pair into hours and checks it is a valid time on campus
def _parse_block(block, day_index):
    if not isinstance(block, (list, tuple)) or len(block) != 2:
        raise ValueError(f"day {day_index}: expected a (start, end) pair, got {block!r}")

    # Half filled in, like (9, None), is a mistake rather than a day off
    if block[0] is None or block[1] is None:
        raise ValueError(f"day {day_index}: start and end must both be set, got {block!r}")

    start = to_hours(block[0])
    end = to_hours(block[1])

    # Zero length or backwards times are rejected, same as User.set_day_schedule
    if end - start <= EPSILON:
        raise ValueError(f"day {day_index}: start must be before end, got {block!r}")

    return start, end


# Converts one day entry into an (arrival, departure) pair in hours, or None.
# A day can be a single (start, end) pair, or a list of pairs if the person
# leaves and comes back. With several pairs, the commute is the first arrival
# and the last departure.
def parse_day(day, day_index=0):
    if _is_empty_day(day):
        return None

    if isinstance(day, str):
        return _parse_block(_split_record(day, day_index), day_index)

    if not isinstance(day, (list, tuple)):
        raise ValueError(f"day {day_index}: expected None or a (start, end) pair, got {day!r}")

    # A single pair, like (9, 17) or ("9:00", "5:00 PM")
    if len(day) == 2 and all(_is_time_value(part) or part is None for part in day):
        return _parse_block(day, day_index)

    # Otherwise it should be a list of pairs
    blocks = [_parse_block(block, day_index) for block in day if not _is_empty_day(block)]
    if not blocks:
        return None

    arrival = min(start for start, end in blocks)
    departure = max(end for start, end in blocks)
    return arrival, departure


# Turns a day stored as text, like "(9,17)" or "{9,17}", into a pair of strings
def _split_record(text, day_index):
    text = text.strip().strip('"').strip()

    if len(text) < 2 or (text[0], text[-1]) not in (("(", ")"), ("{", "}")):
        raise ValueError(f"day {day_index}: could not read {text!r}")

    parts = [part.strip() for part in text[1:-1].split(",")]

    # Postgres writes a missing value in a record as an empty field, e.g. "(9,)"
    return [None if part in ("", "NULL") else part for part in parts]


# Reads a schedule saved by db.insert_user. Postgres stores the Python list as
# array text, e.g. '{"(9,17)",NULL,"(9.5,15.25)",NULL,NULL}', or
# '{{9,17},{9,17},...}' if the days were lists instead of tuples.
def _split_db_array(text):
    text = text.strip()
    if not (text.startswith("{") and text.endswith("}")):
        raise ValueError(f"could not read schedule: {text!r}")

    inner = text[1:-1]
    days = []
    current = ""
    depth = 0
    in_quotes = False

    # Split on commas that are not inside quotes or nested braces
    for char in inner:
        if char == '"':
            in_quotes = not in_quotes
        elif not in_quotes and char == "{":
            depth += 1
        elif not in_quotes and char == "}":
            depth -= 1

        if char == "," and not in_quotes and depth == 0:
            days.append(current)
            current = ""
        else:
            current += char

    if in_quotes or depth != 0:
        raise ValueError(f"could not read schedule: {text!r}")

    if current.strip():
        days.append(current)

    return [day.strip() for day in days]


# Converts a whole schedule into a list of (arrival, departure) pairs or None,
# one per day. Accepts the list form used by User, or the text form stored in
# the database. A missing schedule means no days on campus.
def parse_schedule(schedule):
    if schedule is None:
        return [None] * DAYS_PER_WEEK

    if isinstance(schedule, str):
        schedule = _split_db_array(schedule)

    if not isinstance(schedule, (list, tuple)):
        raise ValueError(f"schedule must be a list of days, got {type(schedule).__name__}")

    if len(schedule) > MAX_DAYS:
        raise ValueError(f"schedule has {len(schedule)} days, at most {MAX_DAYS} allowed")

    days = [parse_day(day, index) for index, day in enumerate(schedule)]

    # A short list just means the remaining days are off
    days += [None] * (DAYS_PER_WEEK - len(days))
    return days


# Checks the tuning values and raises an error if they don't make sense
def _check_tuning(grace, cutoff):
    for name, value in (("grace", grace), ("cutoff", cutoff)):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError(f"{name} must be a finite number, got {value!r}")

    if grace < 0 or cutoff <= grace:
        raise ValueError(f"need 0 <= grace < cutoff, got grace={grace}, cutoff={cutoff}")


# Turns the gap between two times into a value from 0 to 1.
# 1 inside the grace period, 0 at or past the cutoff, linear in between.
def time_closeness(gap, grace=DEFAULT_GRACE_HOURS, cutoff=DEFAULT_CUTOFF_HOURS):
    if gap < 0:
        raise ValueError(f"gap must be non-negative, got {gap}")

    if gap <= grace + EPSILON:
        return 1.0
    if gap >= cutoff - EPSILON:
        return 0.0

    return (cutoff - gap) / (cutoff - grace)


# Scores one day from 0 to 1, given two parsed days.
# Returns None when neither person is on campus, so the day can be skipped.
def day_similarity(day_a, day_b, grace=DEFAULT_GRACE_HOURS, cutoff=DEFAULT_CUTOFF_HOURS):
    if day_a is None and day_b is None:
        return None

    # One person needs a ride and the other isn't going
    if day_a is None or day_b is None:
        return 0.0

    arrival_a, departure_a = day_a
    arrival_b, departure_b = day_b

    morning = time_closeness(abs(arrival_a - arrival_b), grace, cutoff)
    evening = time_closeness(abs(departure_a - departure_b), grace, cutoff)

    return (morning + evening) / 2


# Returns the score for each day from 0 to 1, or None for days that are skipped
def day_scores(schedule_a, schedule_b, grace=DEFAULT_GRACE_HOURS, cutoff=DEFAULT_CUTOFF_HOURS):
    _check_tuning(grace, cutoff)

    days_a = parse_schedule(schedule_a)
    days_b = parse_schedule(schedule_b)

    # Pad the shorter one so a 5 day schedule can be compared with a 7 day one
    length = max(len(days_a), len(days_b))
    days_a += [None] * (length - len(days_a))
    days_b += [None] * (length - len(days_b))

    return [day_similarity(a, b, grace, cutoff) for a, b in zip(days_a, days_b)]


# Returns how compatible two schedules are for sharing rides, from 0 to 100.
# Two schedules with no days on campus at all score 0, since there is
# nothing to match on.
def schedule_similarity(schedule_a, schedule_b, grace=DEFAULT_GRACE_HOURS, cutoff=DEFAULT_CUTOFF_HOURS):
    scores = [score for score in day_scores(schedule_a, schedule_b, grace, cutoff) if score is not None]

    if not scores:
        return 0.0

    result = 100 * sum(scores) / len(scores)

    # Keep floating point error from pushing the result just outside 0 to 100
    return min(100.0, max(0.0, result))
