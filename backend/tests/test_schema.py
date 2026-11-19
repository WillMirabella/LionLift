import psycopg2
import pytest

import db
from models.car import Car
from tests.conftest import USER_COLUMNS, _build_user, _save_user

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


def row_dict(user_id):
    return dict(zip(USER_COLUMNS, db.get_user_by_id(user_id)))


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


# insert_user writes every field of a User, by name
def test_every_user_field_has_a_column():
    names = {name for name, _, _ in columns("users")} - {"id"}
    user = _build_user()
    for field in names:
        assert hasattr(user, field), field


# A bcrypt hash is 60 characters, which must fit in the password column
def test_password_hash_fits():
    from flask_bcrypt import generate_password_hash
    hashed = generate_password_hash("abc12345!").decode()
    _, user_id = _save_user(password=hashed)
    assert row_dict(user_id)["password"] == hashed


# ---- values that must survive a round trip ----

@pytest.mark.parametrize("name", ["José", "Zoë", "Nguyễn", "李", "O'Brien", "Smith-Jones", "a" * 100])
def test_names_round_trip(name):
    _, user_id = _save_user(first_name=name, last_name=name)
    row = row_dict(user_id)
    assert row["first_name"] == name and row["last_name"] == name


def test_empty_and_missing_values_round_trip():
    _, user_id = _save_user(description="", major=None, grad_year=None, street=None)
    row = row_dict(user_id)
    assert row["description"] == "" and row["major"] is None and row["grad_year"] is None and row["street"] is None


@pytest.mark.parametrize("lat, lng", [(40.1175, -75.1091), (0.0, 0.0), (-33.8688, 151.2093), (89.9999, -179.9999)])
def test_coordinates_round_trip(lat, lng):
    _, user_id = _save_user(latitude=lat, longitude=lng)
    row = row_dict(user_id)
    assert (float(row["latitude"]), float(row["longitude"])) == (lat, lng)


def test_car_round_trip():
    car = Car(None, "Toyota", "Corolla", "Silver", 2020, 5)
    assert db.get_car_by_id(car.id)[1:] == ("Toyota", "Corolla", "Silver", 2020, 5)


def test_contact_needs_both_users():
    _, user_id = _save_user()
    with pytest.raises(psycopg2.errors.ForeignKeyViolation):
        db.insert_contact(user_id, 999_999, "text", "2026-11-18")


def test_car_id_must_exist():
    user = _build_user()
    user.car_id = 999_999
    with pytest.raises(psycopg2.errors.ForeignKeyViolation):
        db.insert_user(user)


# ---- known size limits (recorded, not fixed here) ----

# Known issue: descriptions are VARCHAR(100), so a normal-length bio can't be saved
@pytest.mark.xfail(raises=psycopg2.errors.StringDataRightTruncation, reason="users.description is VARCHAR(100)")
def test_bio_longer_than_100_characters():
    _save_user(description="I commute from Jenkintown and can usually leave by 5. " * 3)


# Known issue: a full week of times like "9:30 AM" is about 140 characters stored,
# but users.schedule is VARCHAR(100)
@pytest.mark.xfail(raises=psycopg2.errors.StringDataRightTruncation, reason="users.schedule is VARCHAR(100)")
def test_full_week_of_text_times_fits():
    _save_user(schedule=[("9:30 AM", "5:00 PM")] * 5)


# Known issue: sign-in accepts emails up to 254 characters, but users.email is VARCHAR(100)
@pytest.mark.xfail(raises=psycopg2.errors.StringDataRightTruncation, reason="users.email is VARCHAR(100), email_verifications.email is 254")
def test_long_verified_email_can_make_an_account():
    email = "a" * 120 + "@psu.edu"
    db.save_verification_code(email, "0" * 64, None)
    _save_user(email)
