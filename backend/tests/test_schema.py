import psycopg2
import pytest

import db
from models.car import Car
from models.user import User

# Column order the code reads users in (same as conftest.py and user_search.py)
USER_COLUMNS = (
    "id", "first_name", "last_name", "phone", "email", "gender", "description",
    "grad_year", "major", "schedule", "address", "preferred_payment", "car_id",
)

# Checks that the database tables match what the code expects, and that every
# field survives being saved and read back, including edge values.

pytestmark = pytest.mark.db


def columns(table):
    conn = db.get_connection()
    curr = conn.cursor()
    curr.execute("""
        SELECT column_name, data_type, character_maximum_length
        FROM information_schema.columns WHERE table_name = %s ORDER BY ordinal_position;
    """, (table,))
    rows = curr.fetchall()
    conn.close()
    return rows


def make_user(email="jd@psu.edu", **changes):
    fields = dict(first_name="John", last_name="Doe", phone="2155550100", gender="male",
                  description="hi", grad_year=2028, major="Computer Science", schedule=None)
    fields.update(changes)
    return User(None, email=email, **fields)


# ---- table layout ----

# The users table must list its columns in the order the code reads them
def test_users_column_order():
    assert tuple(name for name, _, _ in columns("users")) == USER_COLUMNS


def test_verification_table_layout():
    layout = {name: (kind, length) for name, kind, length in columns("email_verifications")}
    assert layout["email"] == ("character varying", 254)
    assert layout["code_hash"] == ("character", 64)
    assert layout["attempts"][0] == "integer"
    assert layout["expires_at"][0] == layout["last_sent_at"][0] == "timestamp with time zone"


def test_every_user_field_has_a_column():
    names = {name for name, _, _ in columns("users")}
    user = make_user()
    for field in ("first_name", "last_name", "phone", "email", "gender", "description",
                  "grad_year", "major", "schedule", "address", "preferred_payment", "car_id"):
        assert hasattr(user, field) and field in names


# ---- values that must survive a round trip ----

@pytest.mark.parametrize("name", ["José", "Zoë", "Nguyễn", "李", "O'Brien", "Smith-Jones", "a" * 100])
def test_names_round_trip(name):
    user = make_user(first_name=name, last_name=name)
    row = db.get_user_by_id(user.id)
    assert row[1] == name and row[2] == name


def test_empty_and_missing_values_round_trip():
    user = make_user(description="", major=None, grad_year=None)
    row = dict(zip(USER_COLUMNS, db.get_user_by_id(user.id)))
    assert row["description"] == "" and row["major"] is None and row["grad_year"] is None


def test_update_changes_every_field():
    user = make_user()
    car = Car(None, "Honda", "Civic", "Blue", 2018, 4)
    user.first_name, user.last_name, user.phone = "Jane", "Roe", "2155550199"
    user.gender, user.description, user.grad_year, user.major = "female", "bio", 2027, "Biology"
    user.make_driver("1 School Ln", "Venmo", car.id)
    row = dict(zip(USER_COLUMNS, db.get_user_by_id(user.id)))
    assert (row["first_name"], row["last_name"], row["phone"], row["gender"]) == ("Jane", "Roe", "2155550199", "female")
    assert (row["description"], row["grad_year"], row["major"]) == ("bio", 2027, "Biology")
    assert (row["address"], row["preferred_payment"], row["car_id"]) == ("1 School Ln", "Venmo", car.id)


def test_car_round_trip():
    car = Car(None, "Toyota", "Corolla", "Silver", 2020, 5)
    assert db.get_car_by_id(car.id)[1:] == ("Toyota", "Corolla", "Silver", 2020, 5)


def test_contact_needs_both_users():
    user = make_user()
    with pytest.raises(psycopg2.errors.ForeignKeyViolation):
        db.insert_contact(user.id, 999_999, "text", "2026-11-11")


def test_car_id_must_exist():
    user = make_user()
    with pytest.raises(psycopg2.errors.ForeignKeyViolation):
        user.make_driver("1 School Ln", "Cash", 999_999)


# ---- known size limits (recorded, not fixed here) ----

# Known issue: descriptions are VARCHAR(100), so a normal-length bio can't be saved
@pytest.mark.xfail(raises=psycopg2.errors.StringDataRightTruncation, reason="users.description is VARCHAR(100)")
def test_bio_longer_than_100_characters():
    make_user(description="I commute from Jenkintown and can usually leave by 5. " * 3)


# Known issue: a full week of times like "9:30 AM" is about 140 characters stored,
# but users.schedule is VARCHAR(100)
@pytest.mark.xfail(raises=psycopg2.errors.StringDataRightTruncation, reason="users.schedule is VARCHAR(100)")
def test_full_week_of_text_times_fits():
    make_user(schedule=[("9:30 AM", "5:00 PM")] * 5)


# Known issue: sign-in accepts emails up to 254 characters, but users.email is VARCHAR(100)
@pytest.mark.xfail(raises=psycopg2.errors.StringDataRightTruncation, reason="users.email is VARCHAR(100), email_verifications.email is 254")
def test_long_verified_email_can_make_an_account():
    email = "a" * 120 + "@psu.edu"
    db.save_verification_code(email, "0" * 64, None)
    make_user(email=email)
