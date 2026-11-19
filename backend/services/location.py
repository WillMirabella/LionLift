from geopy.geocoders import Nominatim

def address_to_lat_long(street, city, state, zip):
    geolocator = Nominatim(user_agent="lionlift")

    address = f"{street}, {city}, {state}, {zip}"
    location = geolocator.geocode(address)

    lat = location.latitude if location else None
    long = location.longitude if location else None
    
    return lat, long