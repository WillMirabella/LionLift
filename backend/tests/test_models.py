import pytest

import db
from models.car import Car
from models.user import User

# Tests for models/user.py and models/car.py that don't need a database.


def make_user(**changes):
    fields = dict(first_name="John", last_name="Doe", phone="2155550100", gender="male",
                  description="hi", grad_year=2028, major="Computer Science")
    fields.update(changes)
    return User("jd@psu.edu", "hashed-password", **fields)


# ---- User ----

def test_user_keeps_given_fields():
    user = make_user(street="1 School Ln", city="Abington", state="PA", zip="19001", latitude=40.1, longitude=-75.1)
    assert (user.email, user.password, user.first_name, user.grad_year) == ("jd@psu.edu", "hashed-password", "John", 2028)
    assert (user.street, user.city, user.state, user.zip) == ("1 School Ln", "Abington", "PA", "19001")
    assert (user.latitude, user.longitude) == (40.1, -75.1)


def test_only_email_and_password_are_required():
    user = User("jd@psu.edu", None)
    assert user.first_name is None and user.street is None and user.latitude is None
    assert user.schedule == [None] * 5
    assert user.car_id is None


def test_user_keeps_given_schedule():
    schedule = [(9, 17)] * 5
    assert make_user(schedule=schedule).schedule is schedule


def test_default_schedules_are_not_shared():
    a, b = make_user(), make_user()
    a.set_day_schedule(0, 9, 17)
    assert b.schedule[0] is None


def test_set_day_schedule():
    user = make_user()
    user.set_day_schedule(4, 8, 12.5)
    assert user.schedule[4] == (8, 12.5)


@pytest.mark.parametrize("day, start, end", [
    (-1, 9, 17), (5, 9, 17), (0, 17, 9), (0, 9, 9), (0, -1, 5), (0, 9, 25),
])
def test_set_day_schedule_rejects(day, start, end):
    with pytest.raises(ValueError):
        make_user().set_day_schedule(day, start, end)


def test_make_driver_saves(monkeypatch):
    saved = []
    monkeypatch.setattr(db, "update_user", saved.append)
    user = make_user()
    user.make_driver("Cash", 7)
    assert (user.preferred_payment, user.car_id) == ("Cash", 7)
    assert saved == [user]


def test_to_db_returns_new_id(monkeypatch):
    monkeypatch.setattr(db, "insert_user", lambda user: 42)
    assert make_user().to_db() == 42


def test_user_schedule_similarity():
    a = make_user(schedule=[(9, 17)] * 5)
    b = make_user(schedule=[(9, 17)] * 5)
    c = make_user(schedule=[None] * 5)
    assert a.schedule_similarity(b) == 100.0
    assert a.schedule_similarity(c) == 0.0
    assert a.schedule_similarity(b) == b.schedule_similarity(a)


# ---- known bugs in models/user.py ----

# preferred_payment is a parameter, but __init__ always sets it to None
@pytest.mark.xfail(reason="User.__init__ ignores preferred_payment")
def test_preferred_payment_is_kept():
    assert User("jd@psu.edu", None, preferred_payment="Venmo").preferred_payment == "Venmo"


# __init__ no longer sets id, but __str__ and from_db still use it
@pytest.mark.xfail(raises=AttributeError, reason="User has no id attribute")
def test_user_str_works():
    assert "first_name: John" in str(make_user(schedule=[(9, 17)] + [None] * 4))


# to_db returns the new id but doesn't keep it on the user
@pytest.mark.xfail(raises=AttributeError, reason="to_db doesn't set user.id")
def test_to_db_sets_id(monkeypatch):
    monkeypatch.setattr(db, "insert_user", lambda user: 42)
    user = make_user()
    user.to_db()
    assert user.id == 42


# from_db references an undefined car_id, and reads the row one column off
@pytest.mark.xfail(raises=NameError, reason="User.from_db uses an undefined car_id")
def test_user_from_db(monkeypatch):
    row = (1, "jd@psu.edu", "hash", "John", "Doe", "215", "male", "hi", 2028, "CS",
           None, None, None, "PA", "19001", "40.1", "-75.1", None, None)
    monkeypatch.setattr(db, "get_user_by_id", lambda id: row)
    user = User.from_db(1)
    assert (user.email, user.first_name) == ("jd@psu.edu", "John")


# ---- Car ----

def test_car_fields_and_str():
    car = Car(3, "Toyota", "Camry", "Black", 2024, 4)
    assert (car.id, car.capacity) == (3, 4)
    text = str(car)
    assert "make: Toyota" in text and "capacity: 4" in text


def test_car_from_db(monkeypatch):
    monkeypatch.setattr(db, "get_car_by_id", lambda id: (id, "Honda", "Civic", "White", 2021, 4))
    car = Car.from_db(9)
    assert (car.id, car.make, car.year) == (9, "Honda", 2021)


def test_car_from_db_missing(monkeypatch):
    monkeypatch.setattr(db, "get_car_by_id", lambda id: None)
    assert Car.from_db(9) is None
