import datetime
from dateutil import tz
import re
import requests


def to_datetime(date, mask='%Y-%m-%d %H:%M'):
    if not date:
        return None

    london = tz.gettz('Europe/London')
    date = datetime.datetime.strptime(date, mask).replace(tzinfo=london)
    return date


def deserializer_races_by_track_data(data):
    extracted_data = []
    for track_data in data:
        track = {
            'id': int(track_data['track_id']),
            'name': track_data['track'],
            'country': track_data['races'][0]['country'],
            'races': [],
        }
        for race_data in track_data['races']:
            race = {
                'id': race_data['raceId'],
                'distance': int(re.findall(r'\d+', race_data['distance'])[0]),
                'grade':  race_data['raceGrade'],
                'date': to_datetime(race_data['raceDate']),
            }
            track['races'].append(race)
        extracted_data.append(track)
    return extracted_data


def deserializer_dogs_in_race(data):
    extracted_data = data
    return extracted_data


class RacingPostClient:
    ENDPOINT = 'https://greyhoundbet.racingpost.com'

    # Seria interessante ter um dispatcher para retornar o data correto para cada endpoint?
    def request(self, path, params):
        r = requests.get(self.ENDPOINT + path, params=params)
        json_data = r.json()
        return json_data

    # TODO: Change to get_track_with_races
    def get_races_by_track(self, date):
        path = '/meeting/blocks.sd'
        params = {
            'r_date': date.isoformat(),
            'view': 'time',
            'blocks': 'header,list',
        }

        data = self.request(path, params)

        items_data = data['list']['items']

        return deserializer_races_by_track_data(items_data)

    def get_dogs_in_race(self, id, date):
        path = '/card/blocks.sd'
        params = {
            'race_id': id,
            'r_date': date.isoformat(),
            'tab': 'form',
            'blocks': 'card-header,card-pager,card-tabs,card-title,form',
        }

        data = self.request(path, params)

        dogs_data = data['form']['dogs']

        return deserializer_dogs_in_race(dogs_data)


if __name__ == '__main__':
    import pprint

    racingpost = RacingPostClient()
    tracks = racingpost.get_races_by_track(datetime.date.today())
    dogs = racingpost.get_dogs_in_race(tracks[0]['races'][0]['id'], datetime.date.today())
    # pprint.pprint(races[0])
