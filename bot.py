import os
import json
from random import randrange

import dotenv
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType


class VKinderBot:

    def __init__(self) -> None:
        dotenv.load_dotenv()
        self.token = os.getenv("VK_GROUP_TOKEN")
        self.vk_session = vk_api.VkApi(token=self.token)
        self.longpoll = VkLongPoll(self.vk_session)
        self.create_buttons()

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

    def start_bot(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:

                if event.to_me:
                    request = event.text

                    if request == "Следующий":
                        self.write_msg(event.user_id, f"Следующий")
                    elif request == "Добавить в избранное":
                        self.write_msg(event.user_id, "Добавить в избранное")
                    elif request == "Больше не показывать":
                        self.write_msg(event.user_id, "Больше не показывать")
                    elif request == "Избранное":
                        self.write_msg(event.user_id, "Избранное")
                    elif request == "Начать":
                        self.write_msg(event.user_id, "Туда-сюда, здрасьте-досвидания")
                    else:
                        pass


# if __name__ == '__main__':
#     bot = VKinderBot()
#     bot.start_bot()