import os
import json
from model import ModelProcessor
from search import get_user_info, search_users, get_info

import dotenv
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from threading import Thread


class VKinderBot:

    def __init__(self) -> None:
        dotenv.load_dotenv()
        self.token = os.getenv("VK_GROUP_TOKEN")
        self.auth_link = os.getenv('AUTH_LINK')
        self.vk_session = vk_api.VkApi(token=self.token)
        self.longpoll = VkLongPoll(self.vk_session)
        self.create_main_keyboard()
        self.db = ModelProcessor()

    def create_main_keyboard(self):
        main_keyboard = VkKeyboard()
        main_keyboard.add_button(label='Добавить в избранное', color=VkKeyboardColor.POSITIVE)
        main_keyboard.add_button(label='Следующий', color=VkKeyboardColor.PRIMARY)
        main_keyboard.add_line()
        main_keyboard.add_button(label='Больше не показывать', color=VkKeyboardColor.NEGATIVE)
        main_keyboard.add_button(label='Избранное', color=VkKeyboardColor.SECONDARY)
        main_keyboard = main_keyboard.get_keyboard()
        self.main_keyboard = main_keyboard

    def write_msg(self, user_id, message, keyboard=None):
        if keyboard is None:
            keyboard = self.main_keyboard
        self.vk_session.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': 0, 'keyboard': keyboard})

    def send_person(self, user_id, message, photos, keyboard):
        resp = self.vk_session.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': 0, 'keyboard': keyboard, 'attachment': photos})

    def process_event(self, user_id, text, payload=None):
        request = text.lower()
        user = self.db.user_get(user_id)
        if request == "начать":
            self.button_start(user_id)
        if user is None:
            self.ask_auth(user_id)
            return
        if request == "следующий":
            self.button_next(user)
        elif request == "добавить в избранное":
            self.button_add_to_favourites(user)
        elif request == "больше не показывать":
            self.button_add_to_blacklist(user)
        elif request == "удалить":
            self.button_delete_from_fav(user, payload)
        elif request == "избранное":
            self.button_show_favourites(user)
        else:
            pass

    def ask_auth(self, user_id):
        keyboard = VkKeyboard(inline=True)
        keyboard.add_openlink_button(label='Авторизоваться', link=self.auth_link)
        keyboard = keyboard.get_keyboard()
        msg = 'Для корректной работы требуется авторизация'
        self.write_msg(user_id, msg, keyboard)

    def button_start(self, user_id):
        self.write_msg(user_id, "Добро пожаловать в VKinder бот.")

    def button_next(self, user):
        user_info = get_user_info(user.id)
        person_id, offset = search_users(user.token, user_info, user.offset)
        person_info = get_info(user.token, person_id)
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
        if len(fav_list) == 0:
            self.write_msg(user.id, 'В списке избранного пусто')
            return
        for person_id in fav_list:
            person_info = get_info(user.token, person_id)
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