import os

import psycopg2
import pytest
from hypothesis import HealthCheck, settings

import db

# Shared fixtures for the backend tests.
#
# Tests marked @pytest.mark.db run against a separate database, lionlift_test by
# default, so they never touch the database your app uses. The tables are dropped
# and recreated before every db test.
#
# Settings come from environment variables, with defaults matching db.py:
#   TEST_DB_NAME, TEST_DB_USER, TEST_DB_PASSWORD, TEST_DB_HOST, TEST_DB_PORT
# Set REQUIRE_DB=1 (CI does) to fail instead of skip when Postgres is missing.

DB_SETTINGS = {
    "user": os.environ.get("TEST_DB_USER", "postgres"),
    "password": os.environ.get("TEST_DB_PASSWORD", "password"),
    "host": os.environ.get("TEST_DB_HOST", "127.0.0.1"),
    "port": int(os.environ.get("TEST_DB_PORT", "5432")),
}
TEST_DB_NAME = os.environ.get("TEST_DB_NAME", "lionlift_test")

# Property tests: no time limit per example (CI machines vary in speed), and in
# CI the same examples every run so a failure can always be reproduced
settings.register_profile("default", deadline=None, suppress_health_check=[HealthCheck.too_slow])
settings.register_profile("ci", deadline=None, derandomize=True, max_examples=200,
                          suppress_health_check=[HealthCheck.too_slow])
settings.load_profile("ci" if os.environ.get("CI") else "default")

# Column order of the users table, see create_relations in db.py
USER_COLUMNS = (
    "id", "email", "password", "first_name", "last_name", "phone", "gender", "description",
    "grad_year", "major", "schedule", "street", "city", "state", "zip", "latitude", "longitude",
    "preferred_payment", "car_id",
)


# No test may ever send a real email: Gmail settings from a developer's
# backend/.env are cleared for every test, so send_email only prints
@pytest.fixture(autouse=True)
def _no_real_email(monkeypatch):
    monkeypatch.delenv("GMAIL_ADDRESS", raising=False)
    monkeypatch.delenv("GMAIL_APP_PASSWORD", raising=False)


# Opens a connection to the named database with the test settings
def _connect(database):
    return psycopg2.connect(database=database, connect_timeout=3, **DB_SETTINGS)


# Makes sure the test database exists, once per test run
@pytest.fixture(scope="session")
def test_database():
    try:
        admin = _connect("postgres")
    except psycopg2.OperationalError as error:
        if os.environ.get("REQUIRE_DB") == "1":
            pytest.fail(f"PostgreSQL is required but not reachable: {error}")
        pytest.skip("PostgreSQL is not running, skipping database tests")

    # CREATE DATABASE can't run inside a transaction
    admin.autocommit = True
    curr = admin.cursor()
    curr.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (TEST_DB_NAME,))
    if curr.fetchone() is None:
        curr.execute(f'CREATE DATABASE "{TEST_DB_NAME}";')
    admin.close()
    return TEST_DB_NAME


# Points db.py at the test database and gives each test empty tables
@pytest.fixture
def clean_db(test_database, monkeypatch):
    monkeypatch.setattr(db, "get_connection", lambda: _connect(test_database))
    db.clear_relations()
    db.create_relations()
    return db


# Gives every test marked @pytest.mark.db a clean test database automatically
@pytest.fixture(autouse=True)
def _database_for_db_tests(request):
    if request.node.get_closest_marker("db"):
        request.getfixturevalue("clean_db")


# Builds a row in the same column order as the users table
def _make_row(id, first="Test", last="User", gender=None, grad_year=None, major=None,
             payment=None, car_id=None, phone="5550000000", email=None, schedule=None,
             street="1 Test Ln", description="test", latitude=None, longitude=None):
    values = {
        "id": id, "email": email or f"user{id}@psu.edu", "password": None,
        "first_name": first, "last_name": last, "phone": phone, "gender": gender,
        "description": description, "grad_year": grad_year, "major": major, "schedule": schedule,
        "street": street, "city": "Abington", "state": "PA", "zip": "19001",
        "latitude": latitude, "longitude": longitude, "preferred_payment": payment, "car_id": car_id,
    }
    return tuple(values[column] for column in USER_COLUMNS)


# Gives tests the row builder, e.g. make_row(1, "John", "Doe", grad_year=2028)
@pytest.fixture
def make_row():
    return _make_row


# A small, varied set of rows used by the route tests
@pytest.fixture
def sample_rows():
    make_row = _make_row
    return [
        make_row(1, "John", "Doe", "male", 2028, "Computer Science", "Cash", car_id=1),
        make_row(2, "Bob", "Smith", "Male", 2027, "Biology", "Venmo"),
        make_row(3, "Alice", "Jones", "female", 2028, "computer science", "venmo", car_id=2),
        make_row(4, "Dana", "Lee"),
        make_row(5, "erin", "adams", "female", 2026, "Nursing", "Zelle"),
    ]


# Flask test client for the real app
@pytest.fixture
def client():
    from app import app
    app.config["TESTING"] = True
    return app.test_client()


# Builds a User with every field filled in, in the order User() takes them.
# User doesn't save itself; call save_user to put it in the database.
def _build_user(email="jd@psu.edu", password=None, **changes):
    from models.user import User
    fields = dict(first_name="John", last_name="Doe", phone="2155550100", gender="male",
                  description="hi", grad_year=2028, major="Computer Science", street="1 School Ln",
                  city="Abington", state="PA", zip="19001", latitude=40.1175, longitude=-75.1091,
                  schedule=None)
    fields.update(changes)
    return User(email, password, **fields)


@pytest.fixture
def build_user():
    return _build_user


# Saves a user and returns (user, id). to_db returns the new id but doesn't
# set user.id, so the id is set here for the tests that need it.
def _save_user(email="jd@psu.edu", **changes):
    user = _build_user(email, **changes)
    user.id = user.to_db()
    return user, user.id


@pytest.fixture
def save_user():
    return _save_user
