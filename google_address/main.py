import json
from collections import namedtuple
import requests
from decouple import config


Coordinates = namedtuple("Coordinates", ['lat', 'lng'])


def get_coordinates_from_address(address: str) -> Coordinates:
    api = 'https://maps.googleapis.com/maps/api/geocode/json?address=' + address + '&key='
    url = api + config('GOOGLE_MAPS_API')
    try:
        response = requests.get(url)
    except Exception as e:
        print(e)
        return None
    result = json.loads(response.content.decode("utf-8"))
    var = result['results'][0]['geometry']['location']
    coordinates = Coordinates(var['lat'], var['lng'])
    return coordinates