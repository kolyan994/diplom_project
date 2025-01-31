import vk_api
from pprint import pprint
import os
from dotenv import load_dotenv

load_dotenv()

group_token = os.getenv('VK_GROUP_TOKEN')
vk = vk_api.VkApi(token=group_token).get_api()


def get_api(token):
	return vk_api.VkApi(token=token).get_api()


def get_user_info(user_id):
	user_info = vk.users.get(user_id=user_id, fields='bdate, city, sex')
	return user_info[0]


def search_users(token, user_info, offset, city=1, age_from=18, age_to=30):
	vk2 = get_api(token)
	try:
		city = user_info['city']['id']
	except:
		pass
	try:
		age = user_info['bdate'][-4:]
		age_from = 2023 - 5 - int(age)
		age_to = 2023 + 5 - int(age)
	except:
		pass
	if user_info['sex'] == 1:
		sex = 2
	else:
		sex = 1
	is_closed = True
	while is_closed:
		users_list = vk2.users.search(fields=['is_closed'], city=city, sex=sex, age_from=age_from, age_to=age_to, has_photo=1, count=1, offset=offset)
		is_closed = users_list['items'][0]['is_closed']
		if is_closed:	
			offset += 1
	return users_list['items'][0]['id'], offset


def get_info(token, user_id):
	vk2 = get_api(token)
	photo_data = vk2.photos.get(owner_id=user_id, extended=1, album_id='profile', photo_sizes=1)['items']
	photo_data = sorted(photo_data, key=lambda x: x['likes']['count'], reverse=True)[:3]
	user_data = vk2.users.get(user_id=user_id, fields='city, bdate')
	photos = []
	for photo in photo_data:
		photos.append(photo['id'])
	result = {
		'Имя': f'{user_data[0]["first_name"]} {user_data[0]["last_name"]}',
		'Ссылка': 'https://vk.com/id' + str(user_data[0]['id']),
		'Дата рождения': user_data[0]['bdate'],
		'vk_id': user_data[0]['id'],
		'Фото': photos
	}

	return result