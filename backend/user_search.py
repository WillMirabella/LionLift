import math

# Filters and sorts users for the browse users screen.
#
# A user here is a dict with the same keys as the columns of the users
# relation, in the order db.get_all_users returns them. A user can also have
# "latitude" and "longitude" keys. Users without a valid location can't be
# placed, so they are left out when filtering by distance and always sorted
# last when sorting by distance.

# Column order of the users relation, see create_relations in db.py
USER_COLUMNS = (
    "id", "first_name", "last_name", "phone", "email", "gender", "description",
    "grad_year", "major", "schedule", "address", "preferred_payment", "car_id",
)

# Mean radius of the Earth, used for distances in miles
EARTH_RADIUS_MILES = 3958.8

# Fields users can be sorted by
SORT_KEYS = ("distance", "grad_year", "first_name", "last_name", "major")

# Roles a user can be filtered by. A driver is a user with a car.
ROLES = ("driver", "rider")


# Converts a row from db.get_all_users into a user dict
def row_to_user(row):
    if len(row) != len(USER_COLUMNS):
        raise ValueError(f"expected {len(USER_COLUMNS)} columns, got {len(row)}")
    return dict(zip(USER_COLUMNS, row))


# Lowercases and trims text so comparisons ignore case and extra spaces.
# casefold is used instead of lower so letters like the German ß match too.
def _normalize(text):
    if text is None:
        return None
    return " ".join(str(text).split()).casefold()


# Turns a single value or a list of values into a set of normalized strings.
# Returns None when nothing usable was given, meaning the filter is off.
def _text_set(values):
    if values is None:
        return None
    if not isinstance(values, (list, tuple, set, frozenset)):
        values = [values]

    result = {_normalize(value) for value in values if value is not None}
    result.discard("")
    return result or None


# Checks that a value is a real number and returns it as a float.
# bool is rejected because True and False are ints in Python.
def _to_number(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a number, got {value!r}")
    if not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number, got {value!r}")
    return float(value)


# Checks a latitude and longitude pair and returns it as floats
def check_location(latitude, longitude):
    latitude = _to_number(latitude, "latitude")
    longitude = _to_number(longitude, "longitude")

    if not -90 <= latitude <= 90:
        raise ValueError(f"latitude must be between -90 and 90, got {latitude}")
    if not -180 <= longitude <= 180:
        raise ValueError(f"longitude must be between -180 and 180, got {longitude}")

    return latitude, longitude


# Returns a user's (latitude, longitude), or None if it's missing or invalid
def user_location(user):
    latitude = user.get("latitude")
    longitude = user.get("longitude")
    if latitude is None or longitude is None:
        return None

    try:
        return check_location(latitude, longitude)
    except ValueError:
        return None


# Great-circle distance in miles between two (latitude, longitude) points,
# using the haversine formula
def distance_miles(point_a, point_b):
    lat_a, lon_a = map(math.radians, point_a)
    lat_b, lon_b = map(math.radians, point_b)

    a = (math.sin((lat_b - lat_a) / 2) ** 2
         + math.cos(lat_a) * math.cos(lat_b) * math.sin((lon_b - lon_a) / 2) ** 2)

    # Rounding can push a slightly above 1 for points on opposite sides of the
    # Earth, which would make sqrt(1 - a) fail
    a = min(1.0, max(0.0, a))

    return 2 * EARTH_RADIUS_MILES * math.asin(math.sqrt(a))


# Returns the distance in miles from origin to a user, or None if the user
# has no location
def user_distance(user, origin):
    location = user_location(user)
    if location is None:
        return None
    return distance_miles(origin, location)


# Checks a whole number filter value like a graduation year
def _to_year(value, name):
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be a whole number, got {value!r}")
    return value


# Returns only the users that match every filter that was given.
# Filters left as None are ignored. Text filters ignore case, and a user with
# no value for a field doesn't match a filter on that field.
def filter_users(users, genders=None, majors=None, payments=None, grad_years=None,
                 grad_year_min=None, grad_year_max=None, role=None, name=None,
                 origin=None, max_distance=None, exclude_ids=None):
    genders = _text_set(genders)
    majors = _text_set(majors)
    payments = _text_set(payments)
    name = _normalize(name) or None

    # Specific graduation years, e.g. only 2027 and 2028
    if grad_years is not None:
        if isinstance(grad_years, int):
            grad_years = [grad_years]
        grad_years = {_to_year(year, "grad_years") for year in grad_years} or None

    # A range of graduation years, either end can be left open
    if grad_year_min is not None:
        grad_year_min = _to_year(grad_year_min, "grad_year_min")
    if grad_year_max is not None:
        grad_year_max = _to_year(grad_year_max, "grad_year_max")
    if grad_year_min is not None and grad_year_max is not None and grad_year_min > grad_year_max:
        raise ValueError("grad_year_min can't be after grad_year_max")

    if role is not None:
        role = _normalize(role)
        if role not in ROLES:
            raise ValueError(f"role must be one of {', '.join(ROLES)}, got {role!r}")

    # Distance filtering needs a starting point
    if origin is not None:
        origin = check_location(*origin)
    if max_distance is not None:
        max_distance = _to_number(max_distance, "max_distance")
        if max_distance < 0:
            raise ValueError("max_distance can't be negative")
        if origin is None:
            raise ValueError("max_distance needs an origin to measure from")

    exclude_ids = set(exclude_ids or ())

    result = []
    for user in users:
        if user.get("id") in exclude_ids:
            continue

        if genders is not None and _normalize(user.get("gender")) not in genders:
            continue
        if majors is not None and _normalize(user.get("major")) not in majors:
            continue
        if payments is not None and _normalize(user.get("preferred_payment")) not in payments:
            continue

        # A graduation year that isn't a whole number is treated as missing
        year = user.get("grad_year")
        if isinstance(year, bool) or not isinstance(year, int):
            year = None

        if grad_years is not None and year not in grad_years:
            continue
        if grad_year_min is not None and (year is None or year < grad_year_min):
            continue
        if grad_year_max is not None and (year is None or year > grad_year_max):
            continue

        # Drivers are the users that have a car linked
        if role == "driver" and user.get("car_id") is None:
            continue
        if role == "rider" and user.get("car_id") is not None:
            continue

        # Matches any part of the full name, e.g. "jo" matches John Doe
        if name is not None:
            full_name = _normalize(f"{user.get('first_name') or ''} {user.get('last_name') or ''}")
            if name not in full_name:
                continue

        if max_distance is not None:
            distance = user_distance(user, origin)
            if distance is None or distance > max_distance:
                continue

        result.append(user)

    return result


# Turns text like "distance,-grad_year" into [("distance", False), ("grad_year", True)].
# A leading "-" means descending. Returns an empty list for empty text.
def parse_sort(text):
    if text is None:
        return []

    order = []
    seen = set()
    for part in str(text).split(","):
        part = part.strip()
        if not part:
            continue

        descending = part.startswith("-")
        key = part.lstrip("-+").strip().lower()

        if key not in SORT_KEYS:
            raise ValueError(f"can't sort by {key!r}, options are {', '.join(SORT_KEYS)}")
        if key in seen:
            raise ValueError(f"{key!r} appears more than once in sort")

        seen.add(key)
        order.append((key, descending))

    return order


# Gets the value a user is sorted by for one key, or None if it's missing.
# Text is compared without case so "alice" and "Bob" sort as expected.
def _sort_value(user, key, origin):
    if key == "distance":
        return user_distance(user, origin)

    value = user.get(key)
    if isinstance(value, str):
        value = _normalize(value)
        return value or None
    return value


# Sorts users by a list of (key, descending) pairs, e.g. from parse_sort.
# Earlier pairs take priority. Users missing a value are placed last for that
# key, whether ascending or descending. Ties are broken by last name, first
# name and then id, so the order is always the same for the same users.
def sort_users(users, order=(), origin=None):
    if any(key == "distance" for key, descending in order):
        if origin is None:
            raise ValueError("sorting by distance needs an origin to measure from")
        origin = check_location(*origin)

    result = list(users)

    # Python's sort is stable, so sorting by the lowest priority key first and
    # the highest priority key last gives the combined order
    passes = [("last_name", False), ("first_name", False), ("id", False)]
    passes = list(reversed(passes)) + list(reversed(order))

    for key, descending in passes:
        # Missing values are pulled out so they stay last in both directions
        present = [user for user in result if _sort_value(user, key, origin) is not None]
        missing = [user for user in result if _sort_value(user, key, origin) is None]

        present.sort(key=lambda user: _sort_value(user, key, origin), reverse=descending)
        result = present + missing

    return result


# Filters, then sorts, then adds a "distance" field in miles to each user when
# an origin is given. filters holds the keyword arguments of filter_users,
# other than origin. The users passed in are not changed.
def search_users(users, filters=None, order=(), origin=None):
    filters = dict(filters or {})
    if "origin" in filters:
        raise ValueError("pass origin to search_users directly, not inside filters")
    if origin is not None:
        origin = check_location(*origin)

    matches = filter_users(users, origin=origin, **filters)
    matches = sort_users(matches, order, origin)

    if origin is None:
        return [dict(user) for user in matches]

    result = []
    for user in matches:
        user = dict(user)
        distance = user_distance(user, origin)
        user["distance"] = None if distance is None else round(distance, 2)
        result.append(user)
    return result
