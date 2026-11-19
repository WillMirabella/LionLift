from flask import Blueprint, jsonify, request
import db

# make a blueprint for users
users_bp = Blueprint("users", __name__, url_prefix="/api/users")


# GET /api/users/all
# returns all users' locations
@users_bp.get("/all-locations")
def all_locations():
    return db.get_users_locations()
