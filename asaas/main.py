from datetime import datetime
import requests

access_token = 'xpto'


def listar_faturas(cpf_cnpj):
    url_cliente = 'https://www.asaas.com/api/v3/customers?cpfCnpj=%s' % cpf_cnpj

    data_cliente = requests.get(url_cliente, headers={'access_token': access_token})
    data_cliente = data_cliente.json()

    url_faturas = 'https://www.asaas.com/api/v3/payments?customer=%s' % data_cliente['data'][0]['id']
    data_faturas = requests.get(url_faturas, headers={'access_token' : access_token})
    data_faturas = data_faturas.json()

    return data_faturas


def is_inadimplente(cpf_cnpj):
    # verifica se a pessoa esta com mais de trinta dias de atraso ou com duas faturas atrasadas

    url_cliente = 'https://www.asaas.com/api/v3/customers?cpfCnpj=%s' % cpf_cnpj
    data_cliente = requests.get(url_cliente, headers={'access_token': access_token})
    data_cliente = data_cliente.json()

    url_faturas_atrasadas = 'https://www.asaas.com/api/v3/payments?status=OVERDUE&customer=%s' % data_cliente['data'][0]['id']
    data_faturas_atrasadas = requests.get(url_faturas_atrasadas, headers={'access_token' : access_token})
    data_faturas_atrasadas = data_faturas_atrasadas.json()

    totalCount = data_faturas_atrasadas['totalCount']

    inadimplente = False
    atrasadas = 0
    dias_atraso = 0

    atrasadas = totalCount

    # se tem alguma atrasada
    if atrasadas > 0:
        inadimplente = True

        # calculando dias de atraso
        data_vencimento = data_faturas_atrasadas['data'][0]['dueDate']
        data_vencimento = datetime.strptime(data_vencimento, '%Y-%m-%d').date()
        data_atual = datetime.now().date()

        dias_atraso = (data_atual-data_vencimento).days

    return dict(inadimplente=inadimplente, atrasadas=atrasadas, dias_atraso=dias_atraso)
