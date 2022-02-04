# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import base64
from pprint import pprint

import requests


class BBApiPixV1:

    def __init__(self, server, developer_application_key, client_id, client_secret):
        self.developer_application_key = developer_application_key
        self.access_token = None
        self.header = None

        self.url_oauth = f"https://oauth.{server}/oauth/token"
        self.url_pix = f"https://api.{server}/pix/v1"

        self.basic_auth = self.basic_auth_gen(client_id, client_secret)

    def basic_auth_gen(self, client_id, client_secret):
        text = client_id + ":" + client_secret

        resp = base64.b64encode(text.encode('ascii')).decode('ascii')

        pprint(f"Basic AUTH: {resp}")
        return resp

    def get_token(self):
        headers = {
            'Authorization': "Basic " + self.basic_auth,
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        data = {
            'grant_type': 'client_credentials',
            'code': self.developer_application_key,

        }
        pprint(self.url_oauth)
        resp = requests.post(self.url_oauth, data=data, headers=headers, verify=False)
        if resp.status_code not in (200, 201):
            pprint(self.url_oauth)
            raise RuntimeError(f'Não conseguiu gerar o token de autenticação: {resp.status_code}: {resp.content}')

        json_resp = resp.json()

        self.access_token = json_resp['access_token']

        self.header = {
            'Authorization': 'Bearer ' + self.access_token,
            #Mesmo na produção é para usar esse
            'x-developer-application-key': self.developer_application_key

        }

    def do_get(self, url, params, **kwargs):
        params_str = [f"{key}={value}" for key, value in params.items()]
        params_str = "&".join(params_str)
        pprint(params_str)

        url_param = f"{url}?{params_str}"
        pprint(url_param)

        rspnc = requests.get(url_param, headers=self.header, **kwargs)

        if 200 != rspnc.status_code:
            raise RuntimeError(f"Error [{url_param}] - ({rspnc.status_code}) - {rspnc.content}")
        pprint(rspnc)
        json_resp = rspnc.json()

        return json_resp

    def get_pix_recebidos(self, dthr_ini, dthr_fim):

        url = self.url_pix + "/pix"
        data = {
            'inicio': '2021-12-20T00:00:01Z',
            'fim': "2021-12-24T23:59:59Z",
            # 'gw-app-key':     ### Informado no Header. Não precisaa aqui
        }

        rspnc = self.do_get(url, data, verify=False)

        pprint(rspnc)


    # não consegui fazer paginar
    def get_pix_recebidos_paginacao(self, dthr_ini, dthr_fim):

        url = self.url_pix + "/pix"
        data = {
            'inicio': dthr_ini,
            'fim': "2021-12-24T23:59:59Z",
            'paginacao.paginaAtual': 1,   # não consegui fazer paginar
            'paginacao.itensPorPagina': 50, # não consegui fazer paginar
            'paginacao.quantidadeDePaginas': 4,  # não consegui fazer paginar
            'paginacao.quantidadeTotalDeItens': 167,  # não consegui fazer paginar
        }

        rspnc = self.do_get(url, data, verify=False)

        pprint(rspnc)


homolog = (
    "sandbox.bb.com.br",
    "d27b377908ffab00136be17d60050656b9a1a5b8",
    "eyJpZCI6ImFmYjk5MDktNTQyZC00ZWNmLThlOSIsImNvZGlnb1B1YmxpY2Fkb3IiOjAsImNvZGlnb1NvZnR3YXJlIjoyODM2OSwic2VxdWVuY2lhbEluc3RhbGFjYW8iOjF9",
    "eyJpZCI6IjA3ZDIzOTgtNGYzYi00MTgzLWFmOTMtNWZjZTUxN2YiLCJjb2RpZ29QdWJsaWNhZG9yIjowLCJjb2RpZ29Tb2Z0d2FyZSI6MjgzNjksInNlcXVlbmNpYWxJbnN0YWxhY2FvIjoxLCJzZXF1ZW5jaWFsQ3JlZGVuY2lhbCI6MSwiYW1iaWVudGUiOiJob21vbG9nYWNhbyIsImlhdCI6MTY0MjY5OTA1MDU5OH0"
    )


if __name__ == '__main__':
    #url, developer_application_key, client_id, client_secret = prod_drocer
    url, developer_application_key, client_id, client_secret = homolog


    api = BBApiPixV1(url, developer_application_key, client_id, client_secret)
    api.get_token()
    dados = api.get_pix_recebidos(2, 3)
    pprint(dados)


