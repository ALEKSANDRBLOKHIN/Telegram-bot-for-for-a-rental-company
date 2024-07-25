import telebot
from config import TOKEN
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from db_connection import get_items_from_db
import time


bot = telebot.TeleBot(TOKEN)
user_data = {}


def create_main_menu():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Добавить фильтр", callback_data='new_filter'))
    markup.add(InlineKeyboardButton("Поиск квартир", callback_data='search'))
    return markup


def create_new_filter_menu(user_id):
    if user_id in user_data:
        user_data[user_id]['current_index'] = 0
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Фильтр по цене", callback_data='price_filter'),
               InlineKeyboardButton("Фильтр по расположению", callback_data='place_filter'))
    markup.add(InlineKeyboardButton("Фильтр по количеству комнат", callback_data='rooms_filter'))
    markup.add(InlineKeyboardButton("Сбросить все параметры", callback_data='delete_filter'))
    return markup


def create_after_filter_menu():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Добавить/измеенить фильтры", callback_data='new_filter'))
    markup.add(InlineKeyboardButton("Поиск квартир с этими параметрами", callback_data='search'))
    return markup


def create_rooms_filter_menu():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Студия", callback_data='1_room'),
               InlineKeyboardButton("2 комнаты", callback_data='2_room'))
    markup.add(InlineKeyboardButton("3 комнаты", callback_data='3_room'),
               InlineKeyboardButton("4 комнаты", callback_data='4_room'))
    markup.add(InlineKeyboardButton("Больше 4 комнат", callback_data='4+_room'))
    return markup


def create_place_filter_menu():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("В Париже", callback_data='in_paris'))
    markup.add(InlineKeyboardButton("В округе Парижа", callback_data='not_in_paris'))
    return markup


def create_tinder_menu():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Следующая", callback_data='search'))
    markup.add(InlineKeyboardButton("Изменить фильтры", callback_data='new_filter'))
    markup.add(InlineKeyboardButton("Мне нравится", callback_data='like'))
    return markup


def create_no_more_appartments_menu():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Смотреть сначала", callback_data='search'))
    markup.add(InlineKeyboardButton("Изменть фильтры", callback_data='new_filter'))
    markup.add(InlineKeyboardButton("Главное меню", callback_data='start'))
    return markup


def create_like_menu():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Да", callback_data='text_to_admin'))
    markup.add(InlineKeyboardButton("Смотреть следующую", callback_data='search'))
    markup.add(InlineKeyboardButton("Главное меню", callback_data='start'))
    return markup


def create_after_like_menu():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Смотреть дальше", callback_data='search'))
    markup.add(InlineKeyboardButton("Главное меню", callback_data='start'))
    return markup


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    user_data[user_id] = {'state': 'start', 'current_index': 0}
    user_data[user_id]['price'] = None
    user_data[user_id]['place'] = None
    user_data[user_id]['rooms'] = None
    user_data[user_id]['time'] = None
    user_data[user_id]['current_index'] = 0

    markup = create_main_menu()
    bot.send_message(message.chat.id, "Здравствуйте, давайте найдем вам квартиру.", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'start')
def handle_start(call):
    user_id = call.from_user.id
    user_data[user_id] = {'state': 'start', 'current_index': 0}
    user_data[user_id]['price'] = None
    user_data[user_id]['place'] = None
    user_data[user_id]['rooms'] = None
    user_data[user_id]['time'] = None
    user_data[user_id]['index'] = 0
    markup = create_main_menu()
    bot.send_message(call.message.chat.id, """Здравствуйте, давайте найдем вам квартиру. Все фильтры обнулены""",
                     reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'new_filter')
def handle_new_filter(call):
    user_id = call.from_user.id
    if user_id not in user_data:
        start(call.message)
    else:
        user_data[user_id]['index'] = 0
        markup = create_new_filter_menu(user_id)
        bot.send_message(call.message.chat.id, "Выберите новый фильтр:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'rooms_filter')
def handle_rooms_filter(call):
    user_id = call.from_user.id
    if user_id not in user_data:
        start(call.message)
    else:
        markup = create_rooms_filter_menu()
        bot.send_message(call.message.chat.id, "Сколько комнат вам нужно", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'place_filter')
def handle_place_filter(call):
    user_id = call.from_user.id
    if user_id not in user_data:
        start(call.message)
    else:
        markup = create_place_filter_menu()
        bot.send_message(call.message.chat.id, "Где вы ищете квартиру", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'price_filter')
def handle_price_filter(call):
    user_id = call.from_user.id
    if user_id not in user_data:
        start(call.message)
    else:
        bot.send_message(call.message.chat.id, """Введите максимальную цену аренды квартиры за месяц 
        (только цифру без значка евро):""")
        user_data[user_id]['state'] = 'awaiting_price'


@bot.message_handler(func=lambda message: user_data.get(message.from_user.id, {}).get('state') == 'awaiting_price')
def handle_price_input(message):
    user_id = message.from_user.id
    try:
        # Пытаемся преобразовать введенный текст в число
        max_price = int(message.text)
        user_data[user_id]['price'] = max_price
        user_data[user_id]['state'] = 'start'
        markup = create_after_filter_menu()
        bot.send_message(message.chat.id, f"Максимальная цена установлена: {max_price}", reply_markup=markup)
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите корректное число. Нужно ввести целое число")


@bot.callback_query_handler(func=lambda call: call.data in ['1_room', '2_room', '3_room', '4_room', '4+_room'])
def handle_rooms_filter(call):
    user_id = call.from_user.id
    if user_id not in user_data:
        start(call.message)
    else:
        if call.data == '1_room':
            user_data[user_id]['rooms'] = 1
        elif call.data == '2_room':
            user_data[user_id]['rooms'] = 2
        elif call.data == '3_room':
            user_data[user_id]['rooms'] = 3
        elif call.data == '4_room':
            user_data[user_id]['rooms'] = 4
        elif call.data == '4+_room':
            user_data[user_id]['rooms'] = 5
        markup = create_after_filter_menu()
        if call.data == '4+_room':
            bot.send_message(call.message.chat.id, f"Вы выбрали: более 4 комнат", reply_markup=markup)
        else:
            bot.send_message(call.message.chat.id, f"Вы выбрали: {user_data[user_id]['rooms']} комнаты(а)",
                             reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in ['in_paris', 'not_in_paris'])
def handle_rooms_filter(call):
    user_id = call.from_user.id
    if user_id not in user_data:
        start(call.message)
    else:
        if call.data == 'in_paris':
            user_data[user_id]['place'] = 1
            markup = create_after_filter_menu()
            bot.send_message(call.message.chat.id, "Вы выбрали: В Париже", reply_markup=markup)
        elif call.data == 'not_in_paris':
            user_data[user_id]['place'] = 0
            markup = create_after_filter_menu()
            bot.send_message(call.message.chat.id, f"Вы выбрали: В пригороде Парижа", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'search')
def send_element(call):
    user_id = call.from_user.id
    if user_id not in user_data:
        start(call.message)
    else:
        # Преобразование current_index к целому числу
        user_data[user_id]['current_index'] = int(user_data[user_id]['current_index'])
        a = get_items_from_db(user_data[user_id]['price'], user_data[user_id]['rooms'], user_data[user_id]['place'],
                              user_data[user_id]['current_index'], 1)
        if a:
            bot.send_message(call.message.chat.id, a[0]['information'])
            urls = a[0]['photo']
            url_list = urls.split()
            user_data[user_id]['current_index'] += 1
            media = [InputMediaPhoto(media=url) for url in url_list]

            markup = create_tinder_menu()
            bot.send_media_group(call.message.chat.id, media=media)
            time.sleep(0.5)
            bot.send_message(call.message.chat.id, "Выберите действие:", reply_markup=markup)
        else:
            user_data[user_id]['current_index'] = 0
            markup = create_no_more_appartments_menu()
            bot.send_message(call.message.chat.id, "Больше нет квартир с данными параметрами", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'like')
def handle_like(call):
    user_id = call.from_user.id
    if user_id not in user_data:
        start(call.message)
    else:
        markup = create_like_menu()
        bot.send_message(call.message.chat.id, """Хотите сообщить об этом нашему риелтору, чтобы мы с вами 
        связались для дальнейшего сотрудничества""", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'text_to_admin')
def handle_text_to_admin(call):
    user_id = call.from_user.id
    if user_id not in user_data:
        start(call.message)
    else:
        user_id = call.message.chat.id
        #976093470
        # 5121295272
        operator_chat_id = '5121295272'
        aaa = 1

        username = call.from_user.username
        # Get the current item from the database based on user data
        user_data_info = user_data.get(user_id)

        a = get_items_from_db(
            user_data_info['price'],
            user_data_info['rooms'],
            user_data_info['place'],
            user_data_info['current_index'] - 1
        )

        bot.send_message(operator_chat_id, f'{a}')
        bot.send_message(operator_chat_id, f'юзернейм если есть @{username}')
        markup = create_after_like_menu()
        bot.send_message(call.message.chat.id, """Мы отпрвавили сообщение нашему риелтору. Внимание у некоторых 
        телеграм аккаутах нет юзернейма,в таком случае вы можете написать нам на прямую @sachabouron """,
                         reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'delete_filter')
def handle_delete_filter(call):
    bot.send_message(call.message.chat.id, f"Все фильтры сброшены, вернемся в главное меню")
    start(call.message)


if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(e)
            time.sleep(1)
