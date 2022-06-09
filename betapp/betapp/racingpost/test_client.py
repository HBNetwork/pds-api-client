import datetime
import json
import pytest
import responses

from pathlib import Path
from .client import RacingPostClient, Forecast


BASE_DIR = Path(__file__).parent


@pytest.fixture
def client():
    return RacingPostClient()


@responses.activate
def test_without_tracks(client):
    responses.add(
        responses.GET,
        'https://greyhoundbet.racingpost.com/meeting/blocks.sd',
        json={'list': {'items': []}}, status=200
    )

    tracks = client.tracks_with_races(datetime.date(2021, 2, 15))
    assert tracks == []


@responses.activate
def test_with_tracks(client):
    with open(BASE_DIR / 'test_with_tracks.json') as f:
        json_data = json.load(f)

    responses.add(
        responses.GET,
        'https://greyhoundbet.racingpost.com/meeting/blocks.sd',
        json=json_data, status=200)


    tracks = client.tracks_with_races(datetime.date(2021, 2, 15))
    assert tracks[0].id == 70

def test_forecast():
    assert Forecast("5/2") == 2.5
    assert repr(Forecast("5/2")) == "Forecast('2.5')"

    assert Forecast("2.5") == 2.5
    assert repr(Forecast("2.5")) == "Forecast('2.5')"

    assert Forecast("") == 0
    assert repr(Forecast("")) == "Forecast('0.0')"

    # assert Forecast("2/1") == 2.0
    # assert Forecast("2") == 2.0
