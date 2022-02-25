import pytest
import responses
import requests
from requests import Response

from bbapilib import BBAuthSandbox, BadCredentials

URL = "https://oauth.sandbox.bb.com.br/oauth/token"

@pytest.fixture
def auth():
    client_id = "id"
    client_secret = "secret"
    developer_key = "key"
    auth = BBAuthSandbox(client_id, client_secret, developer_key)
    return auth


def test_token_initial_none(auth):
    assert auth._token is None


@responses.activate
def test_generate_token(auth):
    responses.add(
        responses.POST,
        URL,
        json={"access_token": "123", "token_type": "Bearer"}
    )

    r = auth(Response())

    assert r.headers == {"Authorization": "Bearer 123",
                         "x-developer-application-key": "key"}

@responses.activate
def test_bad_credentials(auth):
    responses.add(
        responses.POST,
        URL,
        status=401
    )

    with pytest.raises(BadCredentials):
        auth.renew()


def test_expired_token(auth):
    #Auth tem um token válido
    #O token expira pelo tempo.
    #tento fazer uma request
    #tem que renovar o token
    #Faz a requisção novamente.
    #valida sucesso