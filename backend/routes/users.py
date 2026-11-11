from flask import Blueprint, jsonify, request

import db
from user_search import approximate_location, parse_sort, row_to_user, search_users, user_location

# Blueprint for browsing users, with filtering and sorting
users_bp = Blueprint("users", __name__, url_prefix="/api/users")

# Fields left out of the browse list so contact info and home addresses
# aren't shown to everyone
PRIVATE_FIELDS = ("phone", "email", "address")


# Copy of a user with their location snapped to about a mile. Distances are
# measured from this point too, so many searches from different places can't
# be combined to find where someone lives.
def _with_approximate_location(user):
    user = dict(user)
    location = user_location(user)
    if location is None:
        user.pop("latitude", None)
        user.pop("longitude", None)
    else:
        user["latitude"], user["longitude"] = approximate_location(location)
    return user


# Reads a query parameter that can be repeated or comma separated,
# e.g. ?gender=male&gender=female or ?gender=male,female
def _get_list(name):
    values = []
    for value in request.args.getlist(name):
        values += [part.strip() for part in value.split(",") if part.strip()]
    return values or None


# Reads a whole number query parameter, or None if it wasn't given
def _get_int(name):
    value = request.args.get(name, "").strip()
    if not value:
        return None
    try:
        return int(value)
    except ValueError:
        raise ValueError(f"{name} must be a whole number, got {value!r}")


# Reads a decimal number query parameter, or None if it wasn't given
def _get_float(name):
    value = request.args.get(name, "").strip()
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        raise ValueError(f"{name} must be a number, got {value!r}")


# Reads a list of whole numbers, e.g. ?grad_year=2027,2028
def _get_int_list(name):
    values = _get_list(name)
    if values is None:
        return None
    try:
        return [int(value) for value in values]
    except ValueError:
        raise ValueError(f"{name} must be whole numbers, got {values!r}")


# Reads the location to measure distance from. Both lat and lon are needed.
def _get_origin():
    latitude = _get_float("lat")
    longitude = _get_float("lon")
    if latitude is None and longitude is None:
        return None
    if latitude is None or longitude is None:
        raise ValueError("lat and lon must be given together")
    return latitude, longitude


# Returns users matching the filters in the query string, in the requested order.
#
# Filters: gender, major, payment, grad_year, grad_year_min, grad_year_max,
#          role (driver or rider), name, max_distance (miles), exclude (user ids)
# Sorting: sort, e.g. sort=distance or sort=-grad_year,last_name
#          A leading "-" sorts that field in descending order.
# Location: lat and lon, needed for max_distance and sorting by distance
@users_bp.get("/")  # this route would be .../api/users/
def browse_users():
    try:
        filters = {
            "genders": _get_list("gender"),
            "majors": _get_list("major"),
            "payments": _get_list("payment"),
            "grad_years": _get_int_list("grad_year"),
            "grad_year_min": _get_int("grad_year_min"),
            "grad_year_max": _get_int("grad_year_max"),
            "role": request.args.get("role") or None,
            "name": request.args.get("name") or None,
            "max_distance": _get_float("max_distance"),
            "exclude_ids": _get_int_list("exclude"),
        }
        order = parse_sort(request.args.get("sort"))
        origin = _get_origin()
    # Bad input from the client gets a 400 with the reason
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    # Outside the try, so a problem with the stored data is a server error (500),
    # not blamed on the request
    users = [_with_approximate_location(row_to_user(row)) for row in db.get_all_users()]

    try:
        results = search_users(users, filters, order, origin)
    # Filters that don't fit together, e.g. max_distance without lat and lon
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    for user in results:
        for field in PRIVATE_FIELDS:
            user.pop(field, None)

    return jsonify(results)
