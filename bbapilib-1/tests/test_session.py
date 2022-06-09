import pytest
import responses
import requests
from bbapilib import BBAuth, BBSession


@pytest.fixture
def session():
    session = BBSession(
        client_id="1",
        client_secret="2",
        developer_key="3"
    )

    return session

def test_endpoint():
    assert BBSession.ENDPOINT == "https://api.bb.com/pix/v1/"


def test_auth_class(session):
    assert session.auth.client_id == "1"
    assert session.auth.client_secret == "2"
    assert session.auth.developer_key == "3"


def test_auth_class_instance(session):
    assert isinstance(session.auth, BBAuth) is True


def test_request(mocker, session):
    mock_request = mocker.patch("requests.Session.request")

    session.request("get", "/some/path/")

    mock_request.assert_called_with("get", f"{BBSession.ENDPOINT}/some/path/")


@responses.activate
def test_return_request(mocker):
    mock = mocker.patch("bbapilib.BBAuth")
    responses.add(
        responses.GET,
        BBSession.ENDPOINT,
        json={"hello": "world"}
    )
    session = BBSession(
        client_id="1",
        client_secret="2",
        developer_key="3",
        auth_class=mock
    )

    resp = session.request("get")


    assert isinstance(resp, requests.models.Response)