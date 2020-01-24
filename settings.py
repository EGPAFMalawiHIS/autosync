import os

from dotenv import load_dotenv
load_dotenv()

load_dotenv(verbose=True)

from pathlib import Path 
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

REPORTING_API = {
    'protocol': os.environ.get('REPORTING_API_PROTOCOL', 'http'),
    'host': os.environ['REPORTING_API_HOST'],
    'port': os.environ['REPORTING_API_PORT'],
    'username': os.environ['REPORTING_API_USERNAME'],
    'password': os.environ['REPORTING_API_PASSWORD'],
    'type': os.environ['REPORTING_API_TYPE']
}

