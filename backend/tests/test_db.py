import re
import threading
from datetime import datetime, time, timedelta, timezone

import psycopg2
import pytest

import db
import routes.auth as auth
from models.car import Car
from models.user import User
from schedule_similarity import parse_schedule
from tests.conftest import USER_COLUMNS

# Database tests for db.py, the models and the auth routes, against a real
# PostgreSQL test database. Every test starts with empty tables (see conftest.py).

pytestmark = pytest.mark.db


# Saves a user and returns it with its id set (see save_user in conftest.py)
def new_user(email="jd@psu.edu", schedule=None, **changes):
    from tests.conftest import _save_user
    return _save_user(email, schedule=schedule, **changes)[0]


def row_dict(user_id):
    return dict(zip(USER_COLUMNS, db.get_user_by_id(user_id)))


def table_names():
    conn = db.get_connection()
    curr = conn.cursor()
    curr.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
    names = {row[0] for row in curr.fetchall()}
    conn.close()
    return names


# ---- tables ----

def test_create_relations_makes_all_tables():
    assert {"cars", "users", "contacts", "email_verifications"} <= table_names()


def test_create_relations_is_repeatable():
    new_user()
    db.create_relations()
    assert db.get_user_by_id(1) is not None


def test_clear_relations_removes_everything():
    db.clear_relations()
    assert table_names() == set()


# ---- users ----

def test_insert_and_get_user():
    user = new_user()
    row = row_dict(user.id)
    assert row["id"] == user.id
    assert (row["email"], row["first_name"], row["last_name"], row["phone"]) == ("jd@psu.edu", "John", "Doe", "2155550100")
    assert (row["street"], row["city"], row["state"], row["zip"]) == ("1 School Ln", "Abington", "PA", "19001")
    assert row["grad_year"] == 2028


# latitude and longitude are stored as text and read back as numbers
def test_location_round_trip():
    user = new_user(latitude=40.1175, longitude=-75.1091)
    row = row_dict(user.id)
    assert (float(row["latitude"]), float(row["longitude"])) == (40.1175, -75.1091)


def test_get_user_by_email():
    user = new_user("find.me@psu.edu")
    assert db.get_user_by_email("find.me@psu.edu")[0] == user.id
    assert db.get_user_by_email("nobody@psu.edu") is None


def test_get_missing_user():
    assert db.get_user_by_id(999) is None


def test_schedule_round_trip():
    schedule = [(9, 17), None, (9.5, 15.25), None, (8, 12)]
    user = new_user(schedule=schedule)
    assert parse_schedule(row_dict(user.id)["schedule"]) == parse_schedule(schedule)


# Known bug: update_user is an INSERT with its values one column off, so
# make_driver adds a broken second row (or fails) instead of updating the user
@pytest.mark.xfail(raises=psycopg2.Error, reason="update_user inserts instead of updating")
def test_update_user_through_make_driver():
    user = new_user()
    car = Car(None, "Toyota", "Camry", "Black", 2024, 4)
    user.make_driver("Venmo", car.id)
    row = row_dict(user.id)
    assert (row["preferred_payment"], row["car_id"]) == ("Venmo", car.id)


# Known gap: nothing stops two accounts from sharing an email
@pytest.mark.xfail(reason="users.email has no UNIQUE constraint")
def test_duplicate_email_rejected():
    new_user("same@psu.edu")
    with pytest.raises(Exception):
        new_user("same@psu.edu")


# Every way the app can write a time reads back as the same hours
@pytest.mark.parametrize("schedule", [
    [("9:30 AM", "5:00 PM"), None, ("09:30", "17:00"), None, None],
    [(time(9, 30), time(17, 0)), None, (time(9, 30), time(17, 0)), None, None],
    [(9.5, 17), None, (9.5, 17.0), None, None],
])
def test_schedule_formats_round_trip(schedule):
    user = new_user(schedule=schedule)
    stored = row_dict(user.id)["schedule"]
    assert parse_schedule(stored) == [(9.5, 17.0), None, (9.5, 17.0), None, None]


# ---- locations for the map ----

def test_locations_are_close_to_real_ones():
    new_user("a@psu.edu", latitude=40.1, longitude=-75.1)
    new_user("b@psu.edu", latitude=39.95, longitude=-75.16)
    locations = sorted(db.get_users_locations())
    assert len(locations) == 2
    for (lat, lng), (real_lat, real_lng) in zip(locations, [(39.95, -75.16), (40.1, -75.1)]):
        assert abs(lat - real_lat) <= 0.015 + 1e-9 and abs(lng - real_lng) <= 0.015 + 1e-9


def test_users_without_location_are_left_out():
    new_user("a@psu.edu", latitude=None, longitude=None)
    new_user("b@psu.edu", latitude=40.1, longitude=-75.1)
    assert len(db.get_users_locations()) == 1


def test_no_users_no_locations():
    assert db.get_users_locations() == []


# Known privacy bug: each call adds new random noise, so averaging many calls
# finds a home almost exactly. 400 calls land within about 100 feet.
@pytest.mark.xfail(reason="location noise is new on every call, so it averages out")
def test_repeated_requests_dont_reveal_location():
    new_user("a@psu.edu", latitude=40.1, longitude=-75.1)
    samples = [db.get_users_locations()[0] for _ in range(400)]
    mean_lat = sum(lat for lat, _ in samples) / len(samples)
    mean_lng = sum(lng for _, lng in samples) / len(samples)
    # Staying more than about a quarter mile off is the goal
    assert abs(mean_lat - 40.1) > 0.004 or abs(mean_lng + 75.1) > 0.004


# ---- cars and contacts ----

def test_car_round_trip():
    car = Car(None, "Honda", "Civic", "White", 2021, 4)
    assert db.get_car_by_id(car.id) == (car.id, "Honda", "Civic", "White", 2021, 4)
    car.color = "Blue"
    db.update_car(car)
    assert Car.from_db(car.id).color == "Blue"


def test_contact_round_trip():
    a, b = new_user("a@psu.edu"), new_user("b@psu.edu")
    contact_id = db.insert_contact(a.id, b.id, "text", datetime(2026, 10, 29, 12, 0))
    row = db.get_contact_by_id(contact_id)
    assert row[1:4] == (a.id, b.id, "text")


def test_contact_needs_real_users():
    with pytest.raises(psycopg2.errors.ForeignKeyViolation):
        db.insert_contact(998, 999, "text", datetime.now())


# ---- email verification storage ----

def test_save_and_get_verification():
    expires = datetime.now(timezone.utc) + timedelta(minutes=10)
    db.save_verification_code("abc@psu.edu", "h" * 64, expires)
    code_hash, expires_at, attempts, last_sent_at, verified = db.get_verification("abc@psu.edu")
    assert code_hash == "h" * 64 and attempts == 0 and verified is False
    assert abs(expires_at - expires) < timedelta(seconds=1)
    assert last_sent_at is not None


def test_get_missing_verification():
    assert db.get_verification("nobody@psu.edu") is None


def test_increment_and_mark_verified():
    db.save_verification_code("abc@psu.edu", "h" * 64, datetime.now(timezone.utc))
    db.increment_verification_attempts("abc@psu.edu")
    db.increment_verification_attempts("abc@psu.edu")
    assert db.get_verification("abc@psu.edu")[2] == 2
    assert db.is_email_verified("abc@psu.edu") is False
    db.mark_email_verified("abc@psu.edu")
    code_hash, expires_at, _, _, verified = db.get_verification("abc@psu.edu")
    assert verified is True and code_hash is None and expires_at is None
    assert db.is_email_verified("abc@psu.edu") is True


def test_is_email_verified_unknown():
    assert db.is_email_verified("nobody@psu.edu") is False


# ---- auth routes against the real database ----

@pytest.fixture
def outbox(monkeypatch):
    sent = []
    monkeypatch.setattr(auth, "send_email", lambda to, subject, body: sent.append(body))
    return sent


def latest_code(outbox):
    return re.search(r"\b(\d{6})\b", outbox[-1]).group(1)


def test_full_verification_flow(client, outbox):
    assert client.post("/api/auth/request-code", json={"email": "ABC@psu.edu"}).status_code == 200
    assert client.post("/api/auth/request-code", json={"email": "abc@psu.edu"}).status_code == 429
    response = client.post("/api/auth/verify", json={"email": "abc@psu.edu", "code": latest_code(outbox)})
    assert response.get_json() == {"status": "verified"}
    assert db.is_email_verified("abc@psu.edu")


# Known bug: a new code resets the attempt counter, allowing 5 guesses per minute forever
@pytest.mark.xfail(reason="save_verification_code resets attempts to 0 on every resend")
def test_resend_keeps_attempt_count(client, outbox):
    client.post("/api/auth/request-code", json={"email": "abc@psu.edu"})
    code = latest_code(outbox)
    for _ in range(5):
        client.post("/api/auth/verify", json={"email": "abc@psu.edu", "code": "000000" if code != "000000" else "111111"})
    conn = db.get_connection()
    conn.cursor().execute("UPDATE email_verifications SET last_sent_at = NOW() - INTERVAL '2 minutes';")
    conn.commit()
    conn.close()
    client.post("/api/auth/request-code", json={"email": "abc@psu.edu"})
    assert db.get_verification("abc@psu.edu")[2] >= 5


# Known bug: parallel guesses all read the count before any increment lands.
# Not strict because it depends on timing.
@pytest.mark.xfail(strict=False, reason="attempt check and increment are separate steps")
def test_parallel_guesses_respect_limit(client, outbox):
    from app import app
    client.post("/api/auth/request-code", json={"email": "abc@psu.edu"})
    code = latest_code(outbox)
    guess = "000000" if code != "000000" else "111111"
    checked = []
    barrier = threading.Barrier(20)

    def attempt():
        with app.test_client() as own_client:
            barrier.wait()
            body = own_client.post("/api/auth/verify", json={"email": "abc@psu.edu", "code": guess}).get_json()
            checked.append(body.get("error") == "Incorrect code")

    threads = [threading.Thread(target=attempt) for _ in range(20)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert sum(checked) <= 5
