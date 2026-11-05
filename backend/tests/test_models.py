import pytest

import db
from models.car import Car
from models.user import User

# Tests for models/user.py and models/car.py that don't need a database.
# Passing an id skips the insert, so these run anywhere.


def make_user(id=1, schedule=None, **changes):
    fields = dict(first_name="John", last_name="Doe", phone="5550000000", email="jd@psu.edu",
                  gender="male", description="hi", grad_year=2028, major="Computer Science")
    fields.update(changes)
    return User(id, schedule=schedule, **fields)


def test_user_defaults():
    user = make_user()
    assert user.id == 1
    assert user.schedule == [None] * 5
    assert user.address is None and user.preferred_payment is None and user.car_id is None


def test_user_keeps_given_schedule():
    schedule = [(9, 17)] * 5
    assert make_user(schedule=schedule).schedule is schedule


def test_default_schedules_are_not_shared():
    a, b = make_user(1), make_user(2)
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


def test_user_str_lists_days():
    user = make_user(schedule=[(9, 17), None, None, None, (8, 12)])
    text = str(user)
    assert "first_name: John" in text
    assert "monday: 9 - 17" in text and "friday: 8 - 12" in text
    assert "tuesday" not in text


def test_user_str_without_schedule():
    assert "schedule: None" in str(make_user())


def test_make_driver_saves(monkeypatch):
    saved = []
    monkeypatch.setattr(db, "update_user", saved.append)
    user = make_user()
    user.make_driver("1 School Ln", "Cash", 7)
    assert (user.address, user.preferred_payment, user.car_id) == ("1 School Ln", "Cash", 7)
    assert saved == [user]


def test_user_schedule_similarity():
    a = make_user(1, schedule=[(9, 17)] * 5)
    b = make_user(2, schedule=[(9, 17)] * 5)
    c = make_user(3, schedule=[None] * 5)
    assert a.schedule_similarity(b) == 100.0
    assert a.schedule_similarity(c) == 0.0
    assert a.schedule_similarity(b) == b.schedule_similarity(a)


# Known bug: from_db references an undefined car_id and passes the wrong arguments
@pytest.mark.xfail(raises=NameError, reason="User.from_db uses an undefined car_id")
def test_user_from_db(monkeypatch):
    row = (1, "John", "Doe", "555", "jd@psu.edu", "male", "hi", 2028, "CS", None, None, None, None)
    monkeypatch.setattr(db, "get_user_by_id", lambda id: row)
    user = User.from_db(1)
    assert user.first_name == "John"


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
