from . import exceptions

import logging
import requests

LOGGER = logging.getLogger(__name__)

class ApiClient:
    '''An ApiClient for the EMR API.

    This class abstracts away all authentication/authorization operations.
    Users need only think about the operation they want to perform (eg.
    GET /users).

    Example:
        >>> config = {'emr_api_username': 'foobar', 'emr_api_password': 'password'}
        >>> api_client = ApiClient(config)
        >>> api_client.get('/patients')
        [patient, another patient, ...]
    '''
    authorization_key = None    # Cached until it expires

    def __init__(self, config):
        self.config = config

    def get(self, *url_parts, **url_params):
        def request():
            url = self.join_url_parts(url_params)
            return requests.get(url, params=url_params, headers={'Authorization': self.get_authorization_key()})

        return self.execute_api_request(request)

    def join_url_parts(self, url_parts):
        return '/'.join((self.config['emr_api_url'], 'api/v1') + url_parts)

    def get_authorization_key(self):
        if ApiClient.authorization_key:
            return ApiClient.authorization_key

        self.login()
        return ApiClient.authorization_key

    def login(self):
        username = self.config['emr_api_username']
        password = self.config['emr_api_password']

        LOGGER.debug(f'Attempting to login into EMR-API as {username}')
        response = requests.post(self.join_url_parts('auth/login'),
                                 json={'username': username, 'password': password},
                                 headers={'Content-type': 'application/json'})

        data = self.extract_data_from_response(response)
        ApiClient.authorization_key = data['token']
        LOGGER.debug(f"Successfully authenticated on EMR-API as {username} ")

    def execute_api_request(self, api_request_method):
        '''Executes an EMR API request within a login session.'''
        if ApiClient.authorization_key is None:
            self.login()

        def run_request():
            response = api_request_method()
            return self.extract_data_from_response(response)

        try:
            return run_request()
        except exceptions.AuthenticationError:
            self.login()
            return run_request

    def extract_data_from_response(self, response):
        '''Extract data from a requests response.

        NOTE: This only extracts from a successful response, otherwise
        an error is raised.
        '''
        if response.status == 401:
            LOGGER.error(f'Authentication failed: {response.body}')
            raise exceptions.AuthenticationError('EMR API request failed')
        elif response.status not in (200, 201, 204):
            LOGGER.error(f'EMR API request failed: {response.status} - {response.body}')
            raise exceptions.ApiError('EMR API request failed')

        return response.json()
 