import json
import requests
import traceback

from abc import ABC
from logging import Logger
from random import randint
from time import sleep
from urllib.parse import urlunparse, urlencode, quote

from stl.exception.api import ApiException, ForbiddenException


class BaseEndpoint(ABC):
    API_PATH = None
    SOURCE = 'airbnb'

    # initialize the class
    def __init__(self, api_key: str, currency: str, logger: Logger, cors_api_key: str = '', locale: str = 'en'):
        self._api_key = api_key
        self._cors_api_key = cors_api_key
        self._currency = currency
        self._locale = locale
        self._logger = logger

    @staticmethod
    def build_airbnb_url(path: str, query=None):
        if query is not None:
            query = urlencode(query)

        return urlunparse(['https', 'www.airbnb.com', path, None, query, None])

    def _api_request(self, url: str, method: str = 'GET', data=None) -> dict:
        if data is None:
            data = {}

        attempts = 0
        headers = {
            'x-airbnb-api-key': self._api_key,
            'x-cors-proxy-api-key': self._cors_api_key,
            'origin': 'https://www.airbnb.com'
        }
        max_attempts = 3
        while attempts < max_attempts:
            #sleep(0.5)  # do a little throttling
            attempts += 1
            try:
                new_url = 'https://steak.kurokrosk.workers.dev/' + url
                response = requests.request(method, new_url, headers=headers, data=data)
                response.raise_for_status()  # Check for HTTP errors
            except requests.exceptions.HTTPError as errh:
                traceback.print_exc()
                response_json = response.json()
                continue
            except requests.exceptions.ConnectionError as errc:
                #traceback.print_exc()
                self._logger.error('ConnectionError')
                continue
            except requests.exceptions.Timeout as errt:
                traceback.print_exc()
                continue
            except requests.exceptions.RequestException as err:
                traceback.print_exc()
                continue

            response_json = response.json()

            errors = response_json.get('errors')
            if not errors:
                return response_json

            self.__handle_api_error(url, errors, response_json)

        raise ApiException(
            ['Could not complete API {} request to "{}"'.format(method, url)])

    @staticmethod
    def _put_json_param_strings(query: dict):
        """Property format JSON strings for 'variables' & 'extensions' params."""
        query['variables'] = json.dumps(
            query['variables'], separators=(',', ':'))
        query['extensions'] = json.dumps(
            query['extensions'], separators=(',', ':'))

    def __handle_api_error(self, url: str, errors: list, json = None):
        error = errors.pop()
        if isinstance(error, dict):
            if error.get('extensions'):
                if error['extensions'].get('response'):
                    status_code = error['extensions']['response'].get(
                        'statusCode')
                    if status_code == 403:
                        self._logger.critical('403 Forbidden: %s' % url)
                        raise ForbiddenException([error])
                    if status_code >= 500:
                        # sleep for a minute and then make another attempt
                        sleep(60)
                        self._logger.warning(error)
                        return
                elif error['extensions'].get('classification') == 'DataFetchingException':
                    sleep(60)  # sleep for a minute and then make another attempt
                    self._logger.warning(error['message'])
                    return

            if 'please try again' in error['message'].lower():
                sleep(30)  # sleep 30 seconds then make another attempt
                self._logger.warning(error['message'])
                return

        self._logger.error(json)
        raise ApiException(errors)
