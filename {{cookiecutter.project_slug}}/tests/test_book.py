# pylint: disable=missing-module-docstring, missing-function-docstring, redefined-outer-name
import pytest
import requests_mock
from kognitos.bdk.api import NounPhrase
from requests import HTTPError

from {{cookiecutter.project_slug}} import {{ cookiecutter.__base_url_name }}, {{ cookiecutter.__book_class_name }}

API_KEY = "test_api_key"
BASE_URL = {{ cookiecutter.__base_url_name }}


@pytest.fixture
def book():
    return {{ cookiecutter.__book_class_name }}()


def test_api_key_valid(book):
    with requests_mock.Mocker() as m:
        m.get(
            f"{BASE_URL}?appid={API_KEY}&q=London",
            status_code=200,
        )
        book.connect(API_KEY)


def test_api_key_invalid(book):
    with requests_mock.Mocker() as m:
        m.get(
            f"{BASE_URL}?appid={API_KEY}&q=London",
            status_code=401,
            json={"message": "Invalid API key"},
        )
        with pytest.raises(ValueError):
            book.connect(API_KEY)


def test_current_temperature(book):
    with requests_mock.Mocker() as m:
        m.get(
            f"{BASE_URL}?appid={API_KEY}&q=London",
            status_code=200,
        )
        m.get(
            f"{BASE_URL}?q=New%20York&appid={API_KEY}&units=metric",
            json={"cod": 200, "main": {"temp": 20.0}},
        )
        book.connect(API_KEY)
        temperature = book.current_temperature(NounPhrase("New York", []))
        assert temperature == 20.0, "The temperature should be 20.0°C"


def test_get_current_temperature_error_response(book):
    with requests_mock.Mocker() as m:
        m.get(
            f"{BASE_URL}?appid={API_KEY}&q=London",
            status_code=200,
        )
        m.get(
            f"{BASE_URL}?q=NonExistentCity&appid={API_KEY}&units=metric",
            json={"cod": 404, "message": "city not found"},
            status_code=404,
        )
        book.connect(API_KEY)
        with pytest.raises(HTTPError, match=r"^city not found$"):
            book.current_temperature(NounPhrase("NonExistentCity", []))


def test_capitalize_string(book):
    assert book.capitalize_string("matias") == "Matias"
