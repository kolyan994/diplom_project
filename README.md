# Командный проект по курсу «Профессиональная работа с Python»

## Функционал приложения:
### Разработана программа-бот, который выполняет действия:

Используя информацию (возраст, пол, город) о пользователе, который общается с ботом в ВКонтакте, осуществляется поиск других пользователей ВКонтакте для знакомств.
У тех людей, которые подошли под критерии поиска, получаем три самые популярные фотографии в профиле. Популярность определяется по количеству лайков.
Выводим в чат с ботом информацию о пользователе в формате:
- имя и фамилия,
- ссылка на профиль,
- три фотографии в виде attachment(https://dev.vk.com/method/messages.send).
Осуществлена возможность:
- перейти к следующему человеку с помощью кнопки.
- Сохранить пользователя в список избранных.
- Вывести список избранных людей. 

### Для работы программы использованы следующие библиотеки в pycharm:
- python-dotenv
- vk_api
- flask
- requests
- sqlalchemy
- psycopg2-binary

Они указаны в файле requirements.txt

### Также для работы программы необходимо использовать следующие данные из окружения:

- VK_GROUP_TOKEN=...
- USER_DB=...
- PASSWORD_DB=...
- CLIENT_ID=... 
- CLIENT_SECRET=...
- REDIRECT_URI=...
- AUTH_LINK=...
- GROUP_ID=...

они указаны в файле env_example.txt

## Использование приложения:

Для того, чтобы воспользоваться ботом, найдите его по ссылке https://vk.com/club222103356
И напишите любое сообщение, например "Начать"
Далее у вас появятся кнопки для общения с ботом, как на картинке:
![2023-08-31 101924.png](images%2F2023-08-31%20101924.png)

Бот предлагает профили для знакомств согласно заданным критериям
![2023-08-31 102816.png](images%2F2023-08-31%20102816.png)

У пользователя есть возможность добавить человека в **Избранное** и в **Черный список**
А также перейти к следующему профилю.

## Программа имеет следующую структуру:

- images
-   для файла readme

- .gitignore
- bot.py
- env_example.txt
- main.py
- model.py
- README.md
- requirements.txt
- search.py
- server.py

### bot.py
Работа бота в VK.com
В модуле определяется класс ClassVK реализующий логику взаимодействия с API ВКонтакте, для

работы Бота.

### main.py

Основной файл запуска программы
В этом модуле происходит инициализация всех подсистем проекта и реализован главный цикл обработки событий,

на которые реагирует Бот ВКонтакте.



### model.py

Скомпонованный код по бд в одном месте

### search.py

Критерии для поиска бота



### server.py

файл подключения
