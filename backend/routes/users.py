from flask import Blueprint, jsonify, request
import db
from models.user import User
from models.car import Car
from services.location import address_to_lat_long

# make a blueprint for users
users_bp = Blueprint("users", __name__, url_prefix="/api/users")


# GET /api/users/all
# returns all users' locations
@users_bp.get("/all-locations")
def all_locations():
    return db.get_users_locations()

# POST /api/users/update-user   body: { email: "", first_name: "", last_name: "", major: ", graduation_year: "",
#                                       description: "", street: "", city: "", state: "", zip_code: "", schedule: "", 
#                                       driver: "", car_make: "", car_model: "", car_year: "", car_color: ""}
# updates a user's info
@users_bp.post('/update-user')
def update_user():
    data = request.get_json(silent=True) or {}
    
    lat, long = address_to_lat_long(
        data.get('street'), 
        data.get('city'), 
        data.get('state'), 
        data.get('zip_code')
    )

    u = User(data.get('email'), None, data.get('first_name'), data.get('last_name'), None, None, data.get('description'), data.get('graduation_year'), 
             data.get('major'), data.get('street'), data.get('city'), data.get('state'), data.get('zip_code'), lat, long, data.get('schedule'), None, None)

    if(data.get('driver') == "true"): u.make_driver(None, Car(None,data.get('car_make'), data.get('car_model'),data.get('car_year'), data.get('car_color')).id)
    db.update_user(u)

    return jsonify({"status": "User updated successfully "}), 201
