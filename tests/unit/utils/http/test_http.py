import pytest
from pytest import MonkeyPatch

from utils.http import generate_get_http_client, http_get


class DummyResponse:
    body: str

    def __init__(self, body):
        self.body = body

    def read(self) -> str:
        return self.body


class TestHttpGet:
    @pytest.mark.parametrize("response, expected", [(DummyResponse("test"), "test")])
    def test_normal(
        self, monkeypatch: MonkeyPatch, response: DummyResponse, expected: str
    ):
        monkeypatch.setattr("utils.http.http.urlopen", lambda _: response)
        actual = http_get("https://google.com")
        assert actual == expected


class TestGenerateGetHttpClient:
    @pytest.mark.parametrize("response, expected", [(DummyResponse("test"), "test")])
    def test_normal(
        self, monkeypatch: MonkeyPatch, response: DummyResponse, expected: str
    ):

        monkeypatch.setattr("utils.http.http.urlopen", lambda _: response)
        client = generate_get_http_client(5)
        actual0 = client("https://google.com")
        actual1 = client("https://google.com")
        assert actual0 == expected
        assert actual1 == expected
