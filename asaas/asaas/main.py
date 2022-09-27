from datetime import datetime, date
from functools import cache
import requests
from enum import Enum, auto
from attrs import define
from typing import List, Optional
from cattrs import Converter

converter = Converter()

converter.register_unstructure_hook(date, lambda dt: dt.isoformat())
converter.register_structure_hook(date, lambda s, _: date.fromisoformat(s))

def struct(obj, type_):
    return converter.structure(obj, type_)


@define
class Group:
    name: str
    

@define
class Customer:
    object: str
    id: str
    dateCreated: date
    name: str
    email: str
    phone: str
    mobilePhone: str
    address: str
    deleted: bool
    groups: Optional[List[Group]] = None


class AsaasResponse(requests.Response):
    @classmethod
    def cast(cls, r):
        r.__class__ = cls
        return r
    
    @cache
    def json(self, **kwargs):
        return super().json(**kwargs)
    
    @property
    def data(self):
        return self.json()["data"]
    

class AsaasSession(requests.Session):
    ENDPOINT = "https://www.asaas.com/api/v3"
    CAST = AsaasResponse.cast
    
    @classmethod
    def from_token(cls, token):
        session = cls()
        session.headers["access_token"] = token
        return session
    
    def request(self, method, url, *args, **kwargs):
        url = self.ENDPOINT + url # path
        response = super().request(method, url, *args, **kwargs)       
        return self.CAST(response)


class PaymentStatus(Enum):
    OVERDUE = auto
    
    def __str__(self):
        s = super().__str__()
        return s.split(".")[-1]   


class AsaasClient:
    def __init__(self, session):
        self.session = session
    
    @classmethod
    def from_credentials(cls, token):
        session = AsaasSession.from_token(token)
        return cls(session)
    
    def request(self, method, path, params):
        response = self.session.request(method, path, params=params)
        response.raise_for_status()
        return response.data
    
    def id_do_cnpj(self, documento):
        data = self.request("GET", "/customers", params={"cpfCnpj": documento})
        customer, *_ = struct(data, List[Customer])
        return customer.id
    
    def faturas(self, id_cliente, status=None):
        params = {"customer": id_cliente}

        if status is not None:
            params["status"] = status

        return self.request("GET", "/payments", params=params)


class AsaasService:
    def __init__(self, client):
        self.client = client
    
    def faturas_do_cnpj(self, documento):
        return self.client.faturas(self.client.id_do_cnpj(documento))
    
    def is_inadimplente(self, cpf_cnpj):
        # verifica se a pessoa esta com mais de trinta dias de atraso ou com duas faturas atrasadas

        id_cliente = self.client.id_do_cnpj(cpf_cnpj)

        faturas_atrasadas = self.client.faturas(id_cliente, status=PaymentStatus.OVERDUE)
        totalCount = len(faturas_atrasadas)

        inadimplente = False
        atrasadas = 0
        dias_atraso = 0

        atrasadas = totalCount

        # se tem alguma atrasada
        if atrasadas > 0:
            inadimplente = True

            # calculando dias de atraso
            data_vencimento = faturas_atrasadas[0]['dueDate']
            data_vencimento = datetime.strptime(data_vencimento, '%Y-%m-%d').date()
            data_atual = datetime.now().date()

            dias_atraso = (data_atual-data_vencimento).days

        return dict(inadimplente=inadimplente, atrasadas=atrasadas, dias_atraso=dias_atraso)

if __name__ == "__main__":
    access_token = 'xpto'

    service = AsaasService(AsaasClient.from_credentials(access_token))
    print(service.faturas_do_cnpj("1234567890"))
