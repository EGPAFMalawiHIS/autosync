import os

from dotenv import load_dotenv
load_dotenv()

load_dotenv(verbose=True)

from pathlib import Path 
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

EMR_API = {
    'protocol': os.environ.get('EMR_API_PROTOCOL', 'http'),
    'host': os.environ['EMR_API_HOST'],
    'port': os.environ['EMR_API_PORT'],
    'username': os.environ['EMR_API_USERNAME'],
    'password': os.environ['EMR_API_PASSWORD']
}
