import pytest
import responses
import requests
from bbapilib import BBAuth, BBSession


@pytest.fixture
def session():
    return BBSession(None)


def test_endpoint():
    assert BBSession.ENDPOINT == "https://api.bb.com/pix/v1/"


@responses.activate
def test_return_request(session):
    responses.add(
        responses.GET,
        BBSession.ENDPOINT,
        json={"hello": "world"}
    )

    resp = session.request("get")

    assert resp.json() == {"hello": "world"}