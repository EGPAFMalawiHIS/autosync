from . import exceptions

import logging
import requests

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

class ApiClient:
    '''An ApiClient for the EMR API.

    This class abstracts away all authentication/authorization operations.
    Users need only think about the operation they want to perform (eg.
    GET /users).

    Example:
        >>> config = {'username': 'foobar', 'password': 'password'}
        >>> api_client = ApiClient(config)
        >>> api_client.get('/patients')
        [patient, another patient, ...]
    '''
    authorization_key = None    # Cached until it expires

    def __init__(self, config):
        self.config = config

    def get(self, url, **url_params):
        def request():
            expanded_url = self.expand_url(url)
            LOGGER.debug(f'Performing GET {expanded_url}')
            return requests.get(expanded_url, params=url_params, headers={'Authorization': self.get_authorization_key()})

        return self.execute_api_request(request)

    def expand_url(self, url):
        protocol = self.config.get('protocol', 'http') 
        host = self.config['host']
        port = self.config['port']
        version = self.config.get('version', 'v1') 

        return f'{protocol}://{host}:{port}/api/{version}/{url}'

    def get_authorization_key(self):
        if ApiClient.authorization_key:
            return ApiClient.authorization_key

        self.login()
        return ApiClient.authorization_key

    def login(self):
        username = self.config['username']
        password = self.config['password']

        LOGGER.debug(f'Attempting to login into EMR-API as {username}')
        response = requests.post(self.expand_url('auth/login'),
                                 json={'username': username, 'password': password},
                                 headers={'Content-type': 'application/json'})

        data = self.extract_data_from_response(response)
        ApiClient.authorization_key = data['authorization']['token']
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
            return run_request()

    def extract_data_from_response(self, response):
        '''Extract data from a requests response.

        NOTE: This only extracts from a successful response, otherwise
        an error is raised.
        '''
        if response.status_code == 200 or response.status_code == 201:
            return response.json()
        elif response.status_code == 204:
            return None # 204 is no content
        elif response.status_code == 401:
            LOGGER.error(f'Authentication failed: {response.body}')
            raise exceptions.AuthenticationError('EMR API request failed')
        else:
            LOGGER.error(f'EMR API request failed: {response.status_code} - {response.text}')
            raise exceptions.ApiError('EMR API request failed')
 