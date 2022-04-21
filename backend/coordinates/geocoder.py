import requests
from django.conf import settings
from requests.exceptions import RequestException

from coordinates.models import Coordinate


def fetch_coordinates(address):
    url = 'https://geocode-maps.yandex.ru/1.x'
    apikey = settings.YANDEX_API_KEY
    params = {
        'geocode': address,
        'apikey': apikey,
        'format': 'json',
    }
    response = requests.get(url, params=params)
    response.raise_for_status()

    found_places = response.json()['response'][
        'GeoObjectCollection'
    ]['featureMember']

    if not found_places:
        return None

    most_relevant_place = found_places[0]
    lon, lat = most_relevant_place['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def add_coordinates(address):
    coordinates = {}
    try:
        lon, lat = fetch_coordinates(address)
    except (RequestException, ValueError):
        pass
    else:
        coordinates.update({
            'lon': lon,
            'lat': lat,
            'are_defined': True
        })
    Coordinate.objects.create(address=address, **coordinates)
