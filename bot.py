import os
import json
from model import ModelProcessor
from search import get_user_info, search_users, get_info

import requests
import dotenv
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from threading import Thread


class VKinderBot:

    def __init__(self) -> None:
        dotenv.load_dotenv()
        self.token = os.getenv("VK_GROUP_TOKEN")
        self.vk_session = vk_api.VkApi(token=self.token)
        self.longpoll = VkLongPoll(self.vk_session)
        self.create_buttons()
        USER = os.getenv('USER_DB')
        PASSWORD = os.getenv('PASSWORD_DB')
        self.db = ModelProcessor(USER, PASSWORD)

    def create_buttons(self):
        def get_but(text, color):
            return {
                "action": {
                    "type": "text",
                    "payload": "{\"button\": \"" + "1" + "\"}",
                    "label": f"{text}"
                },
                "color": f"{color}"
            }
 
        main_keyboard = {
            "one_time" : False,
            "buttons" : [
                [get_but('Добавить в избранное', 'positive'), get_but('Следующий', 'primary')],
                [get_but('Больше не показывать', 'negative'), get_but('Избранное', 'secondary')]
            ]
        }
        main_keyboard = json.dumps(main_keyboard, ensure_ascii = False).encode('utf-8')
        self.main_keyboard = str(main_keyboard.decode('utf-8'))

        favourites_keyboard = {
            "one_time" : False,
            "buttons" : [
                [get_but('На главную', 'positive')]
            ]
        }
        favourites_keyboard = json.dumps(favourites_keyboard, ensure_ascii = False).encode('utf-8')
        self.favourites_keyboard = str(favourites_keyboard.decode('utf-8'))

    def write_msg(self, user_id, message):
        self.vk_session.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': 0, 'keyboard': self.main_keyboard})

    def send_person(self, user_id, message, photos, keyboard):
        resp = self.vk_session.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': 0, 'keyboard': keyboard, 'attachment': photos})

    def process_event(self, event):
        request = event.text.lower()
        user = self.db.user_add(event.user_id)
        if request == "следующий":
            self.button_next(user)
        elif request == "добавить в избранное":
            self.button_add_to_favourites(user)
        elif request == "больше не показывать":
            self.button_add_to_blacklist(user)
        elif request == "удалить":
            self.button_delete_from_fav(user, event.payload)
        elif request == "избранное":
            self.button_show_favourites(user)
        elif request == "начать":
            self.button_start(user)
        else:
            pass

    def button_start(self, user):
        self.write_msg(user.id, "Добро пожаловать в VKinder бот.")

    def button_next(self, user):
        user_info = get_user_info(user.id)
        person_id, offset = search_users(user_info, user.offset)
        person_info = get_info(person_id)
        message = f"{person_info['Имя']}\n{person_info['Ссылка']}\n{person_info['Дата рождения']}"
        photos_list = list()
        for photo_id in person_info['Фото']:
            photos_list.append(f'photo{person_id}_{photo_id}_{self.token}')
        photos = ','.join(photos_list)
        self.send_person(user.id, message, photos, self.main_keyboard)
        user.offset = offset + 1
        user.last_person = person_id
        self.db.user_update(user)

    def button_add_to_favourites(self, user):
        msg = ''
        if user.last_person != 0:
            try:
                self.db.favourites_add(user.id)
                msg = 'Добавлено в избранное'
            except:
                msg = 'Уже в избранном'
        else:
            msg = 'Не удалось добавить'
        self.write_msg(user.id, msg)

    def button_add_to_blacklist(self, user):
        msg = ''
        if user.last_person != 0:
            try:
                self.db.blacklist_add(user.id)
                msg = 'Добавлено'
            except:
                msg = 'Уже в списке'
        else:
            msg = 'Не удалось добавить'
        self.write_msg(user.id, msg)

    def button_show_favourites(self, user):
        fav_list = self.db.favourites_get(user.id)
        for person_id in fav_list:
            person_info = get_info(person_id)
            message = f"{person_info['Имя']}\n{person_info['Ссылка']}\n{person_info['Дата рождения']}"
            photos_list = list()
            for photo_id in person_info['Фото']:
                photos_list.append(f'photo{person_id}_{photo_id}_{self.token}')
            photos = ','.join(photos_list)
            keyboard = VkKeyboard(inline=True)
            keyboard.add_button(payload=person_id, label='Удалить')
            self.send_person(user.id, message, photos, keyboard.get_keyboard())


    def button_delete_from_fav(self, user, delete_id):
        self.db.favourites_delete(user.id, delete_id)
        self.write_msg(user.id, 'Пользователь удален из избранного')

    def start_bot(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    th = Thread(target=self.process_event, args=(event,))
                    th.start()