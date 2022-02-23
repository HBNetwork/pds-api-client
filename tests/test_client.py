from unittest.mock import Mock
import pytest
from bbapilib import BBClient, BBSession

@pytest.fixture
def client():
    return BBClient.from_credentials("1", "2", "3")


def test_from_credentials(client):
    assert isinstance(client.session, BBSession)


def test_request(client, mocker):
    mock = mocker.patch("bbapilib.BBSession.request")

    client.request("get", "/some/path/")

    mock.assert_called_once_with(
        "get",
        path="/some/path/",
        params=None,
        data=None,
    )

def test_request_raise_for_status(client, mocker):
    mock = mocker.patch("bbapilib.BBSession.request", return_value=Mock(
        raise_for_status=Mock()
    ))

    client.request("get", "/")

    mock.return_value.raise_for_status.assert_called_once()


def test_get_pix_recebidos(client, mocker):
    mock = mocker.patch("bbapilib.BBClient.request")

    client.get_pix_recebidos("dtini", "dtend")

    mock.assert_called_once_with(
        'get',
        data={"inicio": "dtini", "fim": "dtend"}
    )