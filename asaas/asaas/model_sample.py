data = [
        {
            "object": "customer",
            "id": "cus_kOV4UNfRBTui",
            "dataCriada": "2017-02-27",
            "name": "Marcelo Almeida",
            "email": "marcelo.almeida@gmail.com",
            "cpfCnpj": "24971563792",
            "phone": "1132300505",
            "mobilePhone": "11991844145",
            "address": "Av. Paulista",
            "addressNumber": "200",
            "complement": "Sala 502",
            "province": "Centro",
            "postalCode": "01310000",
            "city": "cit_938471928372",
            "deleted": False,
            "additionalEmails": "marcelo.almeida+2@gmail.com;marcelo.almeida3@gmail.com",
            "externalReference": "9237487",
            "notificationDisabled": False,
            "groups": [
                {
                    "name": "Padarias"
                }
            ]
        },
        {
            "object": "customer",
            "id": "cus_ekjsdi38sh2",
            "dateCreated": "2017-02-15",
            "name": "Ricardo Santos",
            "email": "ricardo.santos@gmail.com",
            "cpfCnpj": "45414972478",
            "phone": "1132360909",
            "mobilePhone": "11991844145",
            "address": "Av. Paulista",
            "addressNumber": "200",
            "complement": "Sala 502",
            "province": "Centro",
            "postalCode": "01310000",
            "city": "cit_938471928372",
            "deleted": False,
            "additionalEmails": {},
            "externalReference": "25468786",
            "notificationDisabled": False
        }
    ]

from main import Customer, List
from cattrs import Converter
from datetime import date

c = Converter()

c.register_unstructure_hook(date, lambda dt: dt.isoformat())
c.register_structure_hook(date, lambda s, _: date.fromisoformat(s))

l = c.structure(data, List[Customer])
print(l)

