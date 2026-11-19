import random
import time

import pytest

from schedule_similarity import parse_schedule, schedule_similarity

# Speed checks with generous limits. They catch an accidental slowdown, like
# work that grows with the square of the number of users, not small changes.
# Limits are about 10 times what a laptop needs, so slow CI machines still pass.

pytestmark = pytest.mark.perf


def random_schedule(rng):
    days = []
    for _ in range(5):
        if rng.random() < 0.3:
            days.append(None)
        else:
            start = rng.randint(7 * 4, 14 * 4) / 4
            days.append((start, start + rng.randint(2 * 4, 8 * 4) / 4))
    return days


def timed(work):
    start = time.perf_counter()
    result = work()
    return result, time.perf_counter() - start


# One rider against a whole campus of drivers
def test_matching_5000_users_is_fast():
    rng = random.Random(1)
    rider = random_schedule(rng)
    others = [random_schedule(rng) for _ in range(5000)]
    scores, seconds = timed(lambda: [schedule_similarity(rider, other) for other in others])
    assert len(scores) == 5000
    assert seconds < 2.0, f"took {seconds:.2f}s"


# Schedules read from the database are text and have to be parsed each time
def test_parsing_5000_stored_schedules_is_fast():
    rng = random.Random(2)
    texts = []
    for _ in range(5000):
        days = random_schedule(rng)
        texts.append("{" + ",".join("NULL" if d is None else f'"({d[0]},{d[1]})"' for d in days) + "}")
    parsed, seconds = timed(lambda: [parse_schedule(t) for t in texts])
    assert len(parsed) == 5000
    assert seconds < 2.0, f"took {seconds:.2f}s"


# Twice the users should take about twice as long, not four times
def test_matching_grows_linearly():
    rng = random.Random(3)
    rider = random_schedule(rng)
    small = [random_schedule(rng) for _ in range(2000)]
    large = small * 2
    # Best of three runs, so a busy machine doesn't skew one measurement
    t_small = min(timed(lambda: [schedule_similarity(rider, o) for o in small])[1] for _ in range(3))
    t_large = min(timed(lambda: [schedule_similarity(rider, o) for o in large])[1] for _ in range(3))
    assert t_large < t_small * 4, f"{t_small:.3f}s for 2000, {t_large:.3f}s for 4000"


# Browsing with filters, sorting and distance over a large user list (needs #22/#23)
def test_browse_search_5000_users_is_fast():
    user_search = pytest.importorskip("user_search")
    rng = random.Random(4)
    users = [{
        "id": i, "first_name": f"F{i}", "last_name": f"L{rng.randint(0, 999)}", "phone": None, "email": None,
        "gender": rng.choice(["male", "female", None]), "description": None, "grad_year": rng.randint(2026, 2030),
        "major": rng.choice(["Biology", "Nursing", "Computer Science"]), "schedule": None, "street": None, "city": None, "state": None, "zip": None,
        "preferred_payment": rng.choice(["Cash", "Venmo", None]), "car_id": rng.choice([None, 1]),
        "latitude": 40.1 + rng.uniform(-0.2, 0.2), "longitude": -75.1 + rng.uniform(-0.2, 0.2),
    } for i in range(5000)]
    filters = {"majors": ["biology"], "max_distance": 10}
    order = user_search.parse_sort("distance,-grad_year")
    result, seconds = timed(lambda: user_search.search_users(users, filters, order, (40.1, -75.1)))
    assert all(r["distance"] <= 10 for r in result)
    assert seconds < 2.0, f"took {seconds:.2f}s"
