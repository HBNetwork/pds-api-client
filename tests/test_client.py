import re

import pytest
import responses
from requests import HTTPError

@responses.activate
def test_client_raises_on_failed_status_code(client):
    responses.add("GET", re.compile(r""), status=400)

    with pytest.raises(HTTPError):
        client.request("GET", "/")

@responses.activate
def test_received_pixs_success(client):
    responses.add("GET", re.compile(r".+\?inicio=dtini&fim=dtend"),
                  status=200, match_querystring=True)

    r = client.received_pixs("dtini", "dtend")

    assert r.status_code == 200