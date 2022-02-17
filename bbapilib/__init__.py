# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import base64
from pprint import pprint

import requests


class BBSession(requests.Session):
    _host = 'sandbox.bb.com.br'
    _endpoint = None
    _header = None
    _client_id = None
    _client_secret = None
    _developer_key = None

    def __init__(self, client_id: str, cliente_secret: str, developer_key: str):
        super(BBSession, self).__init__()
        self._endpoint = f"https://api.{self._host}/pix/v1/"
        self._client_secret = cliente_secret
        self._client_id = client_id
        self._developer_key = developer_key

    def request(self, method: str, path='', *args, **kwargs):

        url = f'{self._endpoint}{path}'

        if self._header is None:
            self.authenticate()

        resp = super(BBSession, self).request(method, url, *args, headers=self._header, verify=False, **kwargs)

        return resp

    def generate_basic_auth_token(self):
        text = self._client_id + ":" + self._client_secret
        return base64.b64encode(text.encode('ascii')).decode('ascii')

    def authenticate(self):

        url_oauth = f"https://oauth.{self._host}/oauth/token"

        headers = {
            'Authorization': "Basic " + self.generate_basic_auth_token(),
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        data = {
            'grant_type': 'client_credentials',
            'code': self._developer_key,

        }

        resp = super(BBSession, self).request('post', url_oauth, data=data, headers=headers, verify=False)

        json_resp = resp.json()

        access_token = json_resp['access_token']

        self._header = {
            'Authorization': 'Bearer ' + access_token,
            # Mesmo na produção é para usar esse
            'x-developer-application-key': self._developer_key
        }


class BBSessionProduction(BBSession):
    _host = 'bb.com.br'


class BBClient:
    session = None

    def __init__(self, session):
        self.session = session

    @classmethod
    def from_credentials(cls, client_id, client_secret, developer_key, production=False):
        session_class = BBSession
        if production:
            session_class = BBSessionProduction
        return cls(session_class(client_id, client_secret, developer_key))

    def request(self, method, path='', params=None, data=None, *args, **kwargs):
        resp = self.session.request(method, path=path, params=params, data=data, *args, **kwargs)
        resp.raise_for_status()
        return resp

    def get_pix_recebidos(self, dthr_ini, dthr_fim):

        data = {
            'inicio': dthr_ini,
            'fim': dthr_fim
        }

        rspnc = self.request('get', data=data)

        return rspnc


if __name__ == '__main__':
    data_init = (
        "eyJpZCI6ImFmYjk5MDktNTQyZC00ZWNmLThlOSIsImNvZGlnb1B1YmxpY2Fkb3IiOjAsImNvZGlnb1NvZnR3YXJlIjoyODM2OSwic2VxdWVuY2lhbEluc3RhbGFjYW8iOjF9",
        "eyJpZCI6IjA3ZDIzOTgtNGYzYi00MTgzLWFmOTMtNWZjZTUxN2YiLCJjb2RpZ29QdWJsaWNhZG9yIjowLCJjb2RpZ29Tb2Z0d2FyZSI6MjgzNjksInNlcXVlbmNpYWxJbnN0YWxhY2FvIjoxLCJzZXF1ZW5jaWFsQ3JlZGVuY2lhbCI6MSwiYW1iaWVudGUiOiJob21vbG9nYWNhbyIsImlhdCI6MTY0MjY5OTA1MDU5OH0",
        "d27b377908ffab00136be17d60050656b9a1a5b8",
    )
    client = BBClient.from_credentials(*data_init)
    resp = client.get_pix_recebidos('2021-12-20T00:00:01Z', "2021-12-24T23:59:59Z")
    pprint(resp.json())
