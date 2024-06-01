import requests
from dotenv import load_dotenv
import os

url_wh = os.getenv('DISCORD_WH')


payload = {'content':'Des nouveaux matchs sont disponibles au pronostics sur LolProno'}
response = requests.post(url_wh, json=payload)

