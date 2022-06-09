import re

import pytest
import responses
from requests import HTTPError

URL_SERVICE = "https://api.bb.com/pix/v1/"


@responses.activate
def test_client_raises_on_failed_status_code(client_authenticated):
    responses.add(
        responses.GET,
        URL_SERVICE,
        status=400
    )

    with pytest.raises(HTTPError):
        client_authenticated.request("GET", "")


@responses.activate
def test_received_pixs_success(client_authenticated):
    responses.add("GET", re.compile(r".+\?inicio=dtini&fim=dtend"),
                  status=200, match_querystring=True)

    r = client_authenticated.received_pixs("dtini", "dtend")

    assert r.status_code == 200