import datetime
import re
import requests

from dataclasses import dataclass
from dateutil import tz
from typing import List


class Forecast(float):
    def __new__(cls, value=0):
        if not value:
            value = float(0)
        elif '/' in str(value):
            num, den = value.split('/')
            value = float(num) / float(den)
        return super().__new__(cls, value)

    # pass
    # def __new__(cls, value):
    #     if '/' not in str(value):
    #         value = super().__new__(cls, value)
    #         return value._to_forecast()
    #     # if not value:
    #     #     return cls(0.0)

    #     # if '/' in value:
    #     num, den = value.split('/')
    #     # else:
    #     #     num = value
    #     #     den = 1

    #     value = float(num) / float(den)
    #     value = super().__new__(cls, value)
    #     return value._to_forecast()

    # def _to_forecast(self, value):
    #     return Forecast(value)

    def __repr__(self):
        return "{0}({1!r})".format(self.__class__.__name__, self.__str__())

    def __str__(self):
        return "{:n}".format(self)

    # def _to_float(self, value):
    #     return Forecast(value)


@dataclass
class Race:
    id: int
    distance: int
    grade: str
    date: datetime.datetime


@dataclass
class Track:
    id: int
    name: str
    country: str
    races: List[Race]


@dataclass
class Info:
    forecast: float
    top_speed: str
    best_real_time: str


@dataclass
class Dog:
    id: int
    name: str
    color: str
    gender: str
    birth: datetime.date
    sire: str
    dam: str
    info: Info

def to_datetime(date, mask='%Y-%m-%d %H:%M'):
    if not date:
        return None

    london = tz.gettz('Europe/London')
    date = datetime.datetime.strptime(date, mask).replace(tzinfo=london)
    return date


def deserialize_tracks_with_races(data):
    extracted_data = []
    for track_data in data:
        track = Track(id=int(track_data['track_id']),
                      name=track_data['track'],
                      country=track_data['races'][0]['country'],
                      races=[])
        for race_data in track_data['races']:
            race = Race(id=int(race_data['raceId']),
                        distance=int(re.findall(r'\d+', race_data['distance'])[0]),
                        grade=race_data['raceGrade'],
                        date=to_datetime(race_data['raceDate']))
            track.races.append(race)
        extracted_data.append(track)
    return extracted_data


def deserialize_dogs_in_race(data):
    extracted_data = []

    for dog_data in data:
        dog = Dog(id=int(dog_data['dogId']),
                  name=dog_data['dogName'],
                  color=dog_data['dogColor'],
                  gender=dog_data['dogSex'],
                  birth=to_datetime(dog_data['dateOfBirth'], '%d%b%y'),
                  sire=dog_data['sire'],
                  dam=dog_data['dam'],
                  info=Info(forecast=eval(dog_data['forecast']), # TO DO: check if there a security issue
                                 top_speed=dog_data['topSpeed'],
                                 best_real_time=dog_data['brt']))
        extracted_data.append(dog)

    return extracted_data


class RacingPostClient:
    ENDPOINT = 'https://greyhoundbet.racingpost.com'

    # Seria interessante ter um dispatcher para retornar o data correto para cada endpoint?
    def request(self, path, params):
        r = requests.get(self.ENDPOINT + path, params=params)
        return r.json()

    def tracks_with_races(self, date):
        path = '/meeting/blocks.sd'
        params = {
            'r_date': date.isoformat(),
            'view': 'time',
            'blocks': 'header,list',
        }

        data = self.request(path, params)

        items_data = data['list']['items']

        return deserialize_tracks_with_races(items_data)

    def dogs_in_race(self, id, date):
        path = '/card/blocks.sd'
        params = {
            'race_id': id,
            'r_date': date.isoformat(),
            'tab': 'form',
            'blocks': 'card-header,card-pager,card-tabs,card-title,form',
        }

        data = self.request(path, params)

        dogs_data = data['form']['dogs']

        return deserialize_dogs_in_race(dogs_data)


if __name__ == '__main__':
    import pprint

    racingpost = RacingPostClient()
    tracks = racingpost.tracks_with_races(datetime.date.today())
    dogs = racingpost.dogs_in_race(tracks[0].races[0].id, datetime.date.today())
    pprint.pprint(dogs)
