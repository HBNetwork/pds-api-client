
import requests
from requests.auth import AuthBase


class BBAuth(AuthBase):
    OAUTH_ENDPOINT = "https://oauth.bb.com.br/oauth/token"

    def __init__(self, client_id, client_secret, developer_key):
        self.client_id = client_id
        self.client_secret = client_secret
        self.developer_key = developer_key
        self._token = None
        self.credentials = (client_id, client_secret)

    @property
    def token(self):
        if not self._token:
            self.renew()
        return self._token

    def renew(self):
        data = {
            'grant_type': 'client_credentials',
            'code': self.developer_key,
        }

        resp = requests.post(self.OAUTH_ENDPOINT, data=data, verify=False, auth=self.credentials)

        json_resp = resp.json()

        token = json_resp['access_token']
        token_type = json_resp['token_type']

        self._token = f'{token_type} {token}'

    def __call__(self, r):
        r.headers['Authorization'] = self.token
        r.headers['x-developer-application-key'] = self.developer_key
        return r


class BBAuthSandbox(BBAuth):
    OAUTH_ENDPOINT = "https://oauth.sandbox.bb.com.br/oauth/token"


class BBSession(requests.Session):
    ENDPOINT = "https://api.bb.com/pix/v1/"

    def __init__(self, client_id: str, client_secret: str, developer_key: str, auth_class=BBAuth):
        super().__init__()
        self.auth = auth_class(
            client_id=client_id,
            client_secret=client_secret,
            developer_key=developer_key
        )

    def request(self, method: str, path='', *args, **kwargs):

        url = f'{self.ENDPOINT}{path}'

        resp = super().request(method, url, *args, **kwargs)

        return resp


class BBSessionSandbox(BBSession):
    ENDPOINT = "https://api.sandbox.bb.com.br/pix/v1/"

    def __init__(self, client_id: str, client_secret: str, developer_key: str):
        super().__init__(
            client_id=client_id,
            client_secret=client_secret,
            developer_key=developer_key,
            auth_class=BBAuthSandbox
        )

    def request(self, method: str, path='', *args, **kwargs):
        return super().request(method, path, *args, verify=False, **kwargs)


class BBClient:
    def __init__(self, session):
        self.session = session

    @classmethod
    def from_credentials(cls, client_id, client_secret, developer_key):
        return cls(BBSession(client_id, client_secret, developer_key))

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
    client_id = "eyJpZCI6ImFmYjk5MDktNTQyZC00ZWNmLThlOSIsImNvZGlnb1B1YmxpY2Fkb3IiOjAsImNvZGlnb1NvZnR3YXJlIjoyODM2OSwic2VxdWVuY2lhbEluc3RhbGFjYW8iOjF9x"
    client_secret = "eyJpZCI6IjA3ZDIzOTgtNGYzYi00MTgzLWFmOTMtNWZjZTUxN2YiLCJjb2RpZ29QdWJsaWNhZG9yIjowLCJjb2RpZ29Tb2Z0d2FyZSI6MjgzNjksInNlcXVlbmNpYWxJbnN0YWxhY2FvIjoxLCJzZXF1ZW5jaWFsQ3JlZGVuY2lhbCI6MSwiYW1iaWVudGUiOiJob21vbG9nYWNhbyIsImlhdCI6MTY0MjY5OTA1MDU5OH0"
    developer_key = "d27b377908ffab00136be17d60050656b9a1a5b8"

    client = BBClient(BBSessionSandbox(
        client_id=client_id,
        client_secret=client_secret,
        developer_key=developer_key,
    ))

    resp = client.get_pix_recebidos('2021-12-20T00:00:01Z', "2021-12-24T23:59:59Z")
    
    print(resp.json())

# {"statusCode":401,"error":"Unauthorized","message":"Bad Credentials","attributes":{"error":"Bad Credentials"}}

