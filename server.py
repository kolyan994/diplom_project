import os
from threading import Thread
import time
from model import ModelProcessor

import requests
from flask import Flask, request as r
from dotenv import load_dotenv


app = Flask(__name__)
load_dotenv()


URL = 'https://oauth.vk.com/access_token'
PARAMS = {
    'client_id': os.getenv('CLIENT_ID'),
    'client_secret': os.getenv('CLIENT_SECRET'),
    'redirect_uri': os.getenv('REDIRECT_URI')
}


@app.route('/auth', methods=['GET'])
def get_code():
    code = r.args.get('code')
    print(code)
    th = Thread(target=get_token, args=(code,))
    th.start()
    return 'ok'


def get_token(code):
    params = {**PARAMS}
    params['code'] = code
    time.sleep(0.5)
    response = requests.get(url=URL, params=params).json()
    access_token = response.get('access_token')
    if not access_token is None:
         db = ModelProcessor()
         db.user_add(user_id=response['user_id'], token=access_token)
    print(f'token: {access_token}')

def start_server():
    app.run(host="0.0.0.0", port='80')