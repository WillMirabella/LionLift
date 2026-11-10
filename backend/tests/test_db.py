import re
import threading
from datetime import datetime, time, timedelta, timezone

import pytest

import db
import routes.auth as auth
from models.car import Car
from models.user import User
from schedule_similarity import parse_schedule

# Database tests for db.py, the models and the auth routes, against a real
# PostgreSQL test database. Every test starts with empty tables (see conftest.py).

pytestmark = pytest.mark.db


def new_user(email="jd@psu.edu", schedule=None, **changes):
    fields = dict(first_name="John", last_name="Doe", phone="5550000000", gender="male",
                  description="hi", grad_year=2028, major="Computer Science")
    fields.update(changes)
    return User(None, email=email, schedule=schedule, **fields)


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
    row = db.get_user_by_id(user.id)
    assert row[0] == user.id
    assert row[1:5] == ("John", "Doe", "5550000000", "jd@psu.edu")
    assert row[7] == 2028


def test_get_missing_user():
    assert db.get_user_by_id(999) is None


def test_update_user_through_make_driver():
    user = new_user()
    car = Car(None, "Toyota", "Camry", "Black", 2024, 4)
    user.make_driver("1 School Ln", "Venmo", car.id)
    row = db.get_user_by_id(user.id)
    assert (row[10], row[11], row[12]) == ("1 School Ln", "Venmo", car.id)


def test_schedule_round_trip():
    schedule = [(9, 17), None, (9.5, 15.25), None, (8, 12)]
    user = new_user(schedule=schedule)
    stored = db.get_user_by_id(user.id)[9]
    assert parse_schedule(stored) == parse_schedule(schedule)


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
    stored = db.get_user_by_id(user.id)[9]
    assert parse_schedule(stored) == [(9.5, 17.0), None, (9.5, 17.0), None, None]


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
    with pytest.raises(Exception):
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
