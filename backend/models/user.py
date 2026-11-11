
from schedule_similarity import schedule_similarity
import db

class User:
    def __init__(self, id, first_name, last_name, phone, email, gender, description, grad_year, major, schedule):
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.email = email
        self.gender = gender
        self.description = description
        self.grad_year = grad_year
        self.major = major

        # Five weekday entries, each containing a time pair or None.
        if schedule is None:
            self.schedule = [None] * 5
        else:
            self.schedule = schedule

        self.address = None
        self.preferred_payment = None
        self.car_id = None

        if id is None:
            self.id = self.to_db()
        else:
            self.id = id

    def __str__(self):
        DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday"]
        result = []

        for day_index, day in enumerate(DAYS):
            if self.schedule[day_index] is not None:
                start_time, end_time = self.schedule[day_index]
                result.append(f"\t{day}: {start_time} - {end_time}")

        schedule_str = "\n" if result else str(None)
        schedule_str += "\n".join(result)

        return (
            "id: " + str(self.id) +
            "\nfirst_name: " + self.first_name +
            "\nlast_name: " + self.last_name +
            "\nphone: " + str(self.phone) +
            "\nemail: " + self.email +
            "\ngender: " + self.gender +
            "\ndescription: " + self.description +
            "\ngrad_year: " + str(self.grad_year) +
            "\nmajor: " + self.major +
            "\naddress: " + str(self.address) +
            "\npreferred_payment: " + str(self.preferred_payment) +
            "\nschedule: " + schedule_str +
            "\ncar_id: " + str(self.car_id)
        )

    # Promotes a user to driver.
    def make_driver(self, address, preferred_payment, car_id):
        self.address = address
        self.preferred_payment = preferred_payment
        self.car_id = car_id
        db.update_user(self)

    def set_day_schedule(self, day_index, start_time, end_time):
        if day_index < 0 or day_index > 4:
            raise ValueError("day_index must be between 0 and 4 (inclusive)")
        elif start_time >= end_time:
            raise ValueError("start_time must be less than end_time")
        elif start_time < 0 or start_time > 24 or end_time < 0 or end_time > 24:
            raise ValueError("start_time and end_time must be between 0 and 24 (inclusive)")

        self.schedule[day_index] = (start_time, end_time)

    def schedule_similarity(self, other):
        return schedule_similarity(self.schedule, other.schedule)

    @classmethod
    def from_db(cls, id):
        row = db.get_user_by_id(id)

        if row is None:
            return None

        new_user = cls(
            row[0], row[1], row[2], row[3], row[4],
            row[5], row[6], row[7], row[8], row[9]
        )

        # Restore driver information without triggering another database update.
        new_user.address = row[10]
        new_user.preferred_payment = row[11]
        new_user.car_id = row[12]

        return new_user

    def to_db(self):
        return db.insert_user(self)