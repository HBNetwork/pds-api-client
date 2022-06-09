# Exemplo de retorno da api: https://www.asaas.com/api/v3/customers?cpfCnpj=%s

'''
{
    "object": "list",
    "hasMore": true,
    "totalCount": 50,
    "limit": 10,
    "offset": 0,
    "data": [
        {
            "object": "customer",
            "id": "cus_kOV4UNfRBTui",
            "dateCreated": "2017-02-27",
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
            "deleted": false,
            "additionalEmails": "marcelo.almeida+2@gmail.com;marcelo.almeida3@gmail.com",
            "externalReference": "9237487",
            "notificationDisabled": false,
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
            "deleted": false,
            "additionalEmails": {},
            "externalReference": "25468786",
            "notificationDisabled": false
        }
    ]
}
'''


# Exemplo de retorno da api: https://www.asaas.com/api/v3/payments?customer=%s

'''
    {
      "object": "list",
      "hasMore": false,
      "totalCount": 2,
      "limit": 10,
      "offset": 0,
      "data": [
        {
          "object": "payment",
          "id": "pay_080225913252",
          "dateCreated": "2017-03-10",
          "customer": "cus_G7Dvo4iphUNk",
          "paymentLink": "997152082166122",
          "value": 200,
          "netValue": 195,
          "originalValue": {},
          "interestValue": {},
          "description": {},
          "billingType": "BOLETO",
          "status": "PENDING",
          "dueDate": "2017-03-16",
          "originalDueDate": "2017-03-16",
          "paymentDate": {},
          "clientPaymentDate": {},
          "transactionReceiptUrl": {},
          "nossoNumero": "6453",
          "invoiceUrl": "https://www.asaas.com/i/080225913252",
          "invoiceNumber": "00005101",
          "externalReference": {},
          "deleted": false,
          "bankSlipUrl": "https://www.asaas.com/b/pdf/080225913252",
          "postalService": true,
          "anticipated": false
        },
        {
          "object": "payment",
          "id": "pay_961122153955",
          "dateCreated": "2017-03-08",
          "customer": "cus_twmWzMzoTYoh",
          "paymentLink": {},
          "value": 50,
          "netValue": 45,
          "originalValue": {},
          "interestValue": {},
          "description": "Pedido 001387895",
          "billingType": "CREDIT_CARD",
          "status": "PENDING",
          "dueDate": "2017-04-16",
          "originalDueDate": "2017-04-30",
          "paymentDate": {},
          "clientPaymentDate": {},
          "transactionReceiptUrl": {},
          "nossoNumero": {},
          "invoiceUrl": "https://www.asaas.com/i/961122153955",
          "invoiceNumber": "00005100",
          "externalReference": {},
          "deleted": false,
          "bankSlipUrl": "https://www.asaas.com/b/pdf/961122153955",
          "postalService": false,
          "anticipated": false
        }
      ]
    }
'''


# Exemplo de retorno da api: https://www.asaas.com/api/v3/payments?status=OVERDUE&customer=%s

'''
    {
      "object": "list",
      "hasMore": false,
      "totalCount": 2,
      "limit": 10,
      "offset": 0,
      "data": [
        {
          "object": "payment",
          "id": "pay_080225913252",
          "dateCreated": "2017-03-10",
          "customer": "cus_G7Dvo4iphUNk",
          "paymentLink": "997152082166122",
          "value": 200,
          "netValue": 195,
          "originalValue": {},
          "interestValue": {},
          "description": {},
          "billingType": "BOLETO",
          "status": "PENDING",
          "dueDate": "2017-03-16",
          "originalDueDate": "2017-03-16",
          "paymentDate": {},
          "clientPaymentDate": {},
          "transactionReceiptUrl": {},
          "nossoNumero": "6453",
          "invoiceUrl": "https://www.asaas.com/i/080225913252",
          "invoiceNumber": "00005101",
          "externalReference": {},
          "deleted": false,
          "bankSlipUrl": "https://www.asaas.com/b/pdf/080225913252",
          "postalService": true,
          "anticipated": false
        },
        {
          "object": "payment",
          "id": "pay_961122153955",
          "dateCreated": "2017-03-08",
          "customer": "cus_twmWzMzoTYoh",
          "paymentLink": {},
          "value": 50,
          "netValue": 45,
          "originalValue": {},
          "interestValue": {},
          "description": "Pedido 001387895",
          "billingType": "CREDIT_CARD",
          "status": "PENDING",
          "dueDate": "2017-04-16",
          "originalDueDate": "2017-04-30",
          "paymentDate": {},
          "clientPaymentDate": {},
          "transactionReceiptUrl": {},
          "nossoNumero": {},
          "invoiceUrl": "https://www.asaas.com/i/961122153955",
          "invoiceNumber": "00005100",
          "externalReference": {},
          "deleted": false,
          "bankSlipUrl": "https://www.asaas.com/b/pdf/961122153955",
          "postalService": false,
          "anticipated": false
        }
      ]
    }
'''