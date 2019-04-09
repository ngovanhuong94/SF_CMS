import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
flaskenv_path = os.path.join(os.path.dirname(__file__), '.flaskenv')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

if os.path.exists(flaskenv_path):
    load_dotenv(flaskenv_path)

from blog import create_app

app = create_app('production')
