"""{{cookiecutter.project_description}}"""

import logging
from typing import Optional
from urllib.parse import quote

import requests
from kognitos.bdk.api import ConnectionRequired, NounPhrase
from kognitos.bdk.decorators import book, connect, procedure
from requests import HTTPError

{{ cookiecutter.__base_url_name }} = "http://api.openweathermap.org/data/2.5/weather"
DEFAULT_TIMEOUT = 30

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@book(icon="data/icon.svg", name="{{ cookiecutter.project_name }}", tags=["Example"])
class {{ cookiecutter.__book_class_name }}:
    """{{cookiecutter.project_description}}

    Author:
      {{cookiecutter.author_name}}
    """

    def __init__(self):
        """Initializes an instance of the class.

        :param self: The instance of the class.
        """
        self._base_url = {{ cookiecutter.__base_url_name }}
        self._api_key = None
        self._timeout = float(DEFAULT_TIMEOUT)

    @property
    def timeout(self) -> float:
        """Get the value of the timeout.

        Parameters:
            None

        Returns:
            The value of the timeout.

        """
        return self._timeout

    @timeout.setter
    def timeout(self, timeout: float):
        """Sets the timeout value in milliseconds.

        Args:
            timeout (int): The timeout value to set. Must be a positive integer.

        Raises:
            ValueError: If the timeout value is less than or equal to 0.

        """
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        self._timeout = timeout

    @connect(noun_phrase="api keys", name="Api Keys")
    def connect(self, api_key: str, verify: bool = False):
        """Connects to an API using the provided API key.

        Arguments:
            api_key: The API key to be used for connecting

        Labels:
            api_key: API Key
        
        Example:
            >>> connect {{cookiecutter.project_slug | replace('_', ' ')}} book via api keys with
                    the api key is "my_api_key"
        """
        self._api_key = api_key

        if verify:
            test_url = f"{self._base_url}?appid={self._api_key}&q=London"
            response = requests.get(test_url, timeout=self._timeout)
            if response.status_code == 401:
                response_data = response.json()
                if "Invalid API key" in response_data.get("message", ""):
                    raise ValueError("Invalid API key")


    @procedure("to get the (current temperature) at a city", is_mutation=False)
    def current_temperature(
        self, city: NounPhrase, unit: Optional[NounPhrase] = NounPhrase("metric")
    ) -> float:
        """Fetch the current temperature for a specified city.

        Input Concepts:
            the city: The name of the city. Please refer to ISO 3166 for the state codes or country codes.
            the unit: Unit of measurement. standard, metric and imperial units are available. If you do
                not specify the units, metric units will be applied by default.

        Output Concepts:
            the current temperature: The current temperature in the specified units of measurement, or None if an error occurs.

        Example 1:
            Retrieve the current temperature at London

            >>> get the current temperature at London

        Example 2:
            Retrieve the current temperature at London in Celsius

            >>> get the current temperature at New York with
            ...     the unit is metric
        """
        complete_url = f"{self._base_url}?appid={self._api_key}&q={quote(str(city))}&units={str(unit) if unit else 'metric'}"
        try:
            logger.info("retrieving temperature for %s", str(city))
            response = requests.get(complete_url, timeout=self._timeout)
            weather_data = response.json()
            if weather_data["cod"] == 200:
                temperature = weather_data["main"]["temp"]
                return temperature

            logger.error(
                "error fetching data for %s, response Code: %s",
                str(city),
                weather_data["cod"],
            )
            raise HTTPError(weather_data["message"])
        except requests.Timeout:
            logger.error("request timed out")
            raise
        except requests.RequestException as e:
            logger.error("error occurred: %s", e)
            raise

    @procedure("to capitalize a (string)", connection_required=ConnectionRequired.NEVER, is_mutation=False)
    def capitalize_string(self, string: str) -> str:
        """Capitalizes the input string.

        Input Concepts:
            the string: The string value you want to capitalize.

        Output Concepts:
            the string: The capitalized string.

        Example 1:
            Capitalize the string "tomas"

            >>> capitalize "tomas"

        Example 2:
            Capitalize the string "matias"

            >>> the name is "matias"
            >>> capitalize the name
        """
        return string.capitalize()
