from asaas.main import AsaasClient
from unittest.mock import patch


def test_id_do_cnpj():
    client = AsaasClient.from_credentials("asdf")
    data = [{"id": "o_id"}]

    with patch.object(client, 'request', return_value=data) as mock_method:
        assert client.id_do_cnpj("asdf") == "o_id"    
    