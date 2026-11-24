from geopy.geocoders import Nominatim
import math
import numpy as np

def address_to_lat_long(street, city, state, zip):
    geolocator = Nominatim(user_agent="lionlift")

    address = f"{street}, {city}, {state}, {zip}"
    location = geolocator.geocode(address)

    lat = location.latitude if location else None
    long = location.longitude if location else None
    
    return lat, long

# Source: https://stackoverflow.com/questions/66424638/find-point-distance-from-line-python
def miles_away(current_user_lat, current_user_long, other_user_lat, other_user_long):
    school_lat, school_long = 40.11533, -75.11078
    earth_radius_miles = 3958.8

    # Convert to radians and apply scale latitude
    scale = math.cos(math.radians((current_user_lat + school_lat) / 2))
    p1 = (math.radians(current_user_long) * scale, math.radians(current_user_lat))
    p2 = (math.radians(school_long) * scale, math.radians(school_lat))
    p3 = (math.radians(other_user_long) * scale, math.radians(other_user_lat))

    # Clamp projection to the length of the user's route [p1, p2]
    # This is to makes it so the line from is not p1 to p2 is not infinite
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    len_sq = dx**2 + dy**2
    t = max(0, min(1, ((p3[0] - p1[0]) * dx + (p3[1] - p1[1]) * dy) / len_sq)) if len_sq else 0

    if 0 < t < 1:
        # Get perpendicular distance from p3 to the line from p1 to p2
        nom = abs((p2[0] - p1[0]) * (p1[1] - p3[1]) - (p1[0] - p3[0]) * (p2[1] - p1[1]))
        denom = math.sqrt(len_sq)
        dist = nom / denom
    else:
        # Get the distance from p3 to p1 or p2, whichever is closer
        endpoint = p1 if t == 0 else p2
        dist = math.sqrt((p3[0] - endpoint[0])**2 + (p3[1] - endpoint[1])**2)

    # Convert to miles and return
    return dist * earth_radius_miles