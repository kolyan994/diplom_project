import os
from threading import Thread
import time
from model import ModelProcessor
from bot import VKinderBot

import requests
from flask import Flask, json, request as r
from dotenv import load_dotenv


app = Flask(__name__)
vk_bot = VKinderBot()
load_dotenv()


URL = 'https://oauth.vk.com/access_token'
PARAMS = {
    'client_id': os.getenv('CLIENT_ID'),
    'client_secret': os.getenv('CLIENT_SECRET'),
    'redirect_uri': os.getenv('REDIRECT_URI')
}


@app.route('/callback', methods=['POST'])
async def callback():
    data = json.loads(r.data)
    if "type" not in data:
        return "Nope"
    if data.get('type') != 'message_new':
        return 'ok'
    message = data['object']['message']
    user_id = message['from_id']
    text = message['text']
    payload = message.get('payload')
    th = Thread(target=vk_bot.process_event, args=(user_id, text, payload))
    th.start()
    return 'ok'


@app.route('/auth', methods=['GET'])
async def auth():
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
    host, port = '0.0.0.0', '80'
    app.run(host=host, port=port)