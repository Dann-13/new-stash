import io
import json
import urllib.error
from unittest.mock import patch

import pytest

from opencode_usage.providers import deepseek

SAMPLE = {
    "is_available": True,
    "balance_infos": [
        {
            "currency": "USD",
            "total_balance": "12.50",
            "granted_balance": "2.50",
            "topped_up_balance": "10.00",
        }
    ],
}


class _FakeResponse:
    def __init__(self, payload: dict):
        self._body = json.dumps(payload).encode("utf-8")

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def test_parse_balance_ok():
    b = deepseek._parse_balance(SAMPLE)
    assert b.is_available is True
    assert b.currency == "USD"
    assert b.total == 12.5
    assert b.granted == 2.5
    assert b.topped_up == 10.0


def test_url_es_https():
    assert deepseek.BALANCE_URL.startswith("https://api.deepseek.com/")


def test_sin_clave_falla_con_mensaje_seguro():
    with pytest.raises(deepseek.DeepSeekError) as exc:
        deepseek.fetch_balance("")
    assert "DEEPSEEK_API_KEY" in str(exc.value)


def test_fetch_ok_envia_bearer_y_parsea():
    with patch.object(
        deepseek.urllib.request, "urlopen", return_value=_FakeResponse(SAMPLE)
    ) as mocked:
        b = deepseek.fetch_balance("sk-test-123")
    assert b.total == 12.5
    req = mocked.call_args.args[0]
    assert req.full_url == deepseek.BALANCE_URL
    assert req.get_header("Authorization") == "Bearer sk-test-123"


def test_http_401_no_filtra_la_clave():
    err = urllib.error.HTTPError(
        deepseek.BALANCE_URL, 401, "Unauthorized", {}, io.BytesIO(b"")
    )
    with patch.object(deepseek.urllib.request, "urlopen", side_effect=err):
        with pytest.raises(deepseek.DeepSeekError) as exc:
            deepseek.fetch_balance("sk-secreta-xyz")
    assert "sk-secreta-xyz" not in str(exc.value)
    assert "401" in str(exc.value)


def test_error_de_red_mensaje_generico():
    with patch.object(
        deepseek.urllib.request, "urlopen", side_effect=urllib.error.URLError("boom")
    ):
        with pytest.raises(deepseek.DeepSeekError) as exc:
            deepseek.fetch_balance("sk-secreta-xyz")
    assert "sin conexión" in str(exc.value)
    assert "sk-secreta-xyz" not in str(exc.value)


def test_json_roto_no_tumba():
    class _BadResponse(_FakeResponse):
        def read(self):
            return b"no-json"

    with patch.object(
        deepseek.urllib.request, "urlopen", return_value=_BadResponse({})
    ):
        with pytest.raises(deepseek.DeepSeekError):
            deepseek.fetch_balance("sk-test")


def test_sin_balance_infos():
    with pytest.raises(deepseek.DeepSeekError):
        deepseek._parse_balance({"is_available": False, "balance_infos": []})
