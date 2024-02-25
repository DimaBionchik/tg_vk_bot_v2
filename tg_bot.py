import telebot
from google.oauth2.gdch_credentials import ServiceAccountCredentials

import config
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3 as sl
import my_data_base
import gspread
from google.oauth2 import service_account
import time
states = {}

gl_resp = ""
bot = telebot.TeleBot(config.TOKEN)

gs = gspread.service_account(filename=config.JSON_FILE)
ADMIN_ID = ['718611792', '626220085']
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = service_account.Credentials.from_service_account_file("my-test-project-408312-296aa9c49a83.json", scopes=scope)
client = gspread.authorize(creds)
spreadsheet_url = "https://docs.google.com/spreadsheets/d/1qvu3Wn0RXy3WyyetWimApzzTARtfQwNaajcnowmTdyw/edit#gid=0"
sheet = client.open_by_url(spreadsheet_url).sheet1
sh_connection = gs.open_by_url(config.GOOGLE)
worksheet = sh_connection.sheet1
list_of_list = worksheet.get_all_values()

category = {}
info_dishes = {}
info_new_dishes = []

shop_bag = {}
admin_chat_id = -4102272659
dishes_id = {}

for i in list_of_list[1:]:
    category.setdefault(i[3], []).append(i[0])

for name in list_of_list[1:]:
    info_dishes[name[0]] = ['', name[1], name[2]]

markupANS = InlineKeyboardMarkup().row(InlineKeyboardButton("Да", callback_data="yes"),InlineKeyboardButton("Нет", callback_data="no"))

markupI = InlineKeyboardMarkup()
buttons = [InlineKeyboardButton(name, callback_data=name) for name in category.keys()]
[markupI.row(*buttons[i:i + 2]) for i in range(0, len(buttons), 2)]
if len(buttons) % 2 != 0: markupI.row(buttons[-1])

markup = InlineKeyboardMarkup()
markup.add(InlineKeyboardButton('В меню', callback_data='3'))


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    user_id = call.from_user.id

    if user_id not in states:
        states.setdefault(user_id, {'state': None, 'shop_basket': {}})

    states_shop_basket = states[user_id]['shop_basket']

    if call.data in category:
        message_id = call.message.message_id
        show_dishes_menu(call.data, call.from_user.id, message_id)

    elif call.data[0] == 'f':
        markupL = InlineKeyboardMarkup()
        buttons = [InlineKeyboardButton(item, callback_data='2' + item) for item in category[call.data[1:]]]

        [markupL.row(buttons[i], buttons[i + 1]) for i in range(0, len(buttons) - 1, 2)]

        if len(buttons) % 2 != 0: markupL.row(buttons[-1])
        markupL.add(InlineKeyboardButton('В меню', callback_data='3'))
        bot.send_message(call.message.chat.id, 'Выберите блюдо.', reply_markup=markupL)

    elif call.data[0] == '3':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Выберите категорию блюда ⬇️", reply_markup=markupI)

    elif call.data[0] == '2':
        show_dish_info(call.data[1:], call.message.chat.id)

    elif call.data[0] == '0':
        user_id = call.from_user.id

        # Убедимся, что 'shop_basket' инициализирован как пустой словарь
        if 'shop_basket' not in states[user_id] or states[user_id]['shop_basket'] is None:
            states[user_id]['shop_basket'] = {}

        states[user_id]['shop_basket'][call.data[1:]] = states[user_id]['shop_basket'].get(call.data[1:],
                                                                                           info_dishes[call.data[1:]][
                                                                                           1:] + [0])
        states[user_id]['shop_basket'][call.data[1:]][-1] += 1
        states[user_id]['state'] = "добавление товара"
        print(states)
        markupO = InlineKeyboardMarkup().row(
            InlineKeyboardButton('В меню', callback_data='3'),
            InlineKeyboardButton('Просмотр корзины', callback_data='shop_bag'))
        bot.send_message(call.message.chat.id, 'Товар успешно добавлен.', reply_markup=markupO)

    elif call.data == 'start':
        bot.send_message(-4102272659,
                         "Введите данные для нового блюда в формате:\n1. Категория\n2. Названия\n3. Количество\n4. Время приготовления\n5. Цена (в BYN)",
                         parse_mode='Markdown')
        bot.register_next_step_handler(call.message, enter_dish_adm)


    elif call.data == 'shop_bag':
        states_shop_basket = states[user_id]['shop_basket']

        if states_shop_basket:
            response = '\n'.join(
                [f'{item} [x{details[2]}] = {int(details[1]) * int(details[2])} BYN.' for item, details in
                 states_shop_basket.items()])
            cur = max(int(info_dishes[i][1]) for i in states_shop_basket) if states_shop_basket else 0
            response += f'\nПримерное время доставки: {cur + 10} минут.'
            user_id = call.from_user.id
            states[user_id]['state'] = "юзер в корзине"
            states[user_id]['shop_basket'] = states_shop_basket
            print(states)

            markupG = InlineKeyboardMarkup().row(
                InlineKeyboardButton('Изменить корзину', callback_data='change'),
                InlineKeyboardButton('Очистить корзину', callback_data='clear')).row(
                InlineKeyboardButton('В меню', callback_data='3'),
                InlineKeyboardButton("Оформить заказ", callback_data='order'))

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=f'Ваша корзина 🛒:\n\n{response}', reply_markup=markupG)
        else:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text='Корзина пуста 🛒.', reply_markup=markup)


    elif call.data == 'clear':
        states_shop_basket = states[user_id]['shop_basket']
        states_shop_basket.clear()
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'Корзина пуста 🛒',
                              reply_markup=markup, parse_mode='MarkdownV2')
        user_id = call.from_user.id
        states[user_id]['state'] = "очистка корзины"
        states[user_id]['shop_basket'] = None
        print(states)

    elif call.data == 'change':
        markupG = InlineKeyboardMarkup()
        buttons = [InlineKeyboardButton(dish, callback_data='*' + dish) for dish in states_shop_basket]

        [markupG.row(buttons[i], buttons[i + 1]) for i in range(0, len(buttons) - 1, 2)]

        if len(buttons) % 2 != 0:
            markupG.row(buttons[-1])
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Выберите продукт для изменения 🍴.', reply_markup=markupG)

    elif call.data == "yes":
        answer = bot.send_message(call.message.chat.id, "Спасибо за обратную связь!\nНапишите свой отзыв(не более 300 символов):")
        bot.register_next_step_handler(answer, answers)

    elif call.data == 'no':
        bot.send_message(call.message.chat.id, 'Спасибо за заказ!\nБудем ждать вас еще!')

    elif call.data == "order":
        price, count = 0, 0
        states_shop_basket = states[user_id]['shop_basket']

        for dish, details in states_shop_basket.items():
            name_dishes = dish
            price = price + int(details[1])
            counts = details[2]
            my_data_base.upd(name_dishes, counts)
        count += 1
        response = '\n'.join(
            [f'{item} [x{details[2]}] = {int(details[1]) * int(details[2])} BYN.' for item, details in
             states_shop_basket.items()])
        user_id = call.from_user.id
        states[user_id]['state'] = "Оформление заказа"
        states[user_id]['shop_basket'] = states_shop_basket
        print(states)
        global gl_resp
        gl_resp = response
        cur = max(int(info_dishes[i][1]) for i in states_shop_basket) if states_shop_basket else 0
        response += f'\nПримерное время доставки: {cur + 10} минут.'
        my_data_base.upd_user(user_id, states_shop_basket)
        user_name = call.from_user.username or call.from_user.first_name or call.from_user.last_name
        bot.send_message(chat_id="-4102272659", text=f" Пользователь @{user_name}, оформил заказ :{response} ")
        message = my_data_base.check_dishes()
        bot.send_message(chat_id="-4102272659", text=f" {message} ")
        bot.send_message(call.message.chat.id,
                         f"Ваш заказ №{count}\n____________________\n\nСостав заказа:\n{response}\n\nКонечная стоимость: {price} BYN.")
        states_shop_basket.clear()
        bot.send_message(call.message.chat.id, "Хотите оставить отзыв?", reply_markup=markupANS)
        user_id = call.from_user.id
        states[user_id]['state'] = "Заказ оформлен"
        states[user_id]['shop_basket'] = None
        print(states)

    elif call.data == 'stop':
        markupH = InlineKeyboardMarkup()
        for names in category.keys():
            markupH.add(InlineKeyboardButton(names, callback_data='s' + names))
        bot.send_message(-4102272659, 'Выбери категорию.', reply_markup=markupH)


    elif call.data[0] == 's':
        markupM = InlineKeyboardMarkup()
        for item in category[call.data[1:]]:
            markupM.add(InlineKeyboardButton(item, callback_data='p' + item))
        markupM.add(InlineKeyboardButton('В каталог', callback_data='stop'))
        bot.send_message(-4102272659, "Выбери товар.\nПосле выбора товар будет поставлен на 'stop'.",
                         reply_markup=markupM)

    elif call.data[0] == '*':
        markupG = InlineKeyboardMarkup().row(
            InlineKeyboardButton('-', callback_data='-' + call.data[1:]),
            InlineKeyboardButton('Удалить', callback_data='d' + call.data[1:]),
            InlineKeyboardButton('+', callback_data='+' + call.data[1:])).row(
            InlineKeyboardButton('В меню', callback_data='3'))

        states_shop_basket = states[user_id]['shop_basket']
        dish_info_text = f'{call.data[1:]}.\n\nСтоимость = {int(states_shop_basket[call.data[1:]][1]) * int(states_shop_basket[call.data[1:]][2])} BYN.' + f'\nКоличество = {states_shop_basket[call.data[1:]][2]}.'

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=dish_info_text,
                              reply_markup=markupG)

    for operation in ['-', '+', 'd']:
        if call.data.startswith(operation) and call.data[1:] in states_shop_basket:
            if operation in ['-', '+']:
                states_shop_basket[call.data[1:]][2] = str(int(states_shop_basket[call.data[1:]][2]) + (1 if operation == '+' else -1))
                total_cost = int(states_shop_basket[call.data[1:]][1]) * int(states_shop_basket[call.data[1:]][2])
                dish_info_text = f'{call.data[1:]}\n\nСтоимость = {total_cost} BYN.\nКоличество = {states_shop_basket[call.data[1:]][2]}.'

                markupG = InlineKeyboardMarkup().row(
                    InlineKeyboardButton('-', callback_data='-' + call.data[1:]),
                    InlineKeyboardButton('Удалить', callback_data='d' + call.data[1:]),
                    InlineKeyboardButton('+', callback_data='+' + call.data[1:])).row(
                    InlineKeyboardButton('В меню', callback_data='3'))

                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=dish_info_text, reply_markup=markupG)

            elif operation == 'd':

                del states_shop_basket[call.data[1:]]
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text='Товар успешно удален.', reply_markup=markup)
                user_id = call.from_user.id
                states[user_id]['state'] = "Удаление товаров из корзины"
                states[user_id]['shop_basket'] = states_shop_basket
                print(states)




@bot.message_handler(func=lambda message: message.chat.id == -4102272659, commands=['stop_prod'])
def stop_product(message):
    user_id = message.from_user.id
    if user_id==config.SUPER_ADMIN_ID:
        markupN = InlineKeyboardMarkup()
        markupN.add(InlineKeyboardButton("Каталог", callback_data="stop"))
        bot.send_message(message.chat.id, "Привет!\nДля товара на стоп жми на кнопку ниже.", reply_markup=markupN)
    else:
        bot.send_message(message.chat.id, "У вас недостаточно прав для этой команды ")


def answers(message):
    ans = message.text
    user_id = message.from_user.id
    my_data_base.insert_into_disches_answer(gl_resp, user_id, ans)
    bot.send_message(message.chat.id, "Cпасибо за отзыв, если хотите продолжить жмите /menu")


@bot.message_handler(func=lambda message: message.chat.id == -4102272659, commands=['dish_add'])
def handle_command_in_group(message):
    markupN = InlineKeyboardMarkup()
    markupN.add(InlineKeyboardButton("Start to add", callback_data="start"))
    bot.send_message(message.chat.id,
                     "Привет!\nДля добавления блюда подготовьте всю информацию и нажмите на кнопку ниже.",
                     reply_markup=markupN)


def get_dish_photo(message):
    if message.photo:
        bot.send_message(-4102272659, f"ID отправленной фотографии: {message.photo[-1].file_id}")
        values_to_insert = [info_new_dishes[1], info_new_dishes[3], info_new_dishes[4], info_new_dishes[0]]
        print(values_to_insert)
        my_data_base.insert_into_disches(info_new_dishes[1], info_new_dishes[2], info_new_dishes[3], info_new_dishes[4])

        column_index = 1
        column_values = worksheet.col_values(column_index)
        first_empty_row = next((i for i, value in enumerate(column_values, start=1) if not value), None)

        if first_empty_row is None:
            first_empty_row = len(column_values) + 1
        for i, value in enumerate(values_to_insert, start=1):
            worksheet.update_cell(first_empty_row, column_index + i - 1, value)
        dishes_id[info_new_dishes[1]] = message.photo[-1].file_id
        info_new_dishes.clear()


@bot.message_handler(func=lambda message: message.chat.id == -4102272659, commands=['dish_add'])
def handle_command_in_group(message):
    markupN = InlineKeyboardMarkup()
    markupN.add(InlineKeyboardButton("Start to add", callback_data="start"))
    bot.send_message(message.chat.id,
                     "Привет!\nДля добавления блюда подготовьте всю информацию и нажмите на кнопку ниже.",
                     reply_markup=markupN)


def enter_dish_adm(message):
    info_new_dishes.extend(message.text.split())
    bot.send_message(-4102272659,
                     f"Блюдо добавленно.\nЕго данные:\n{info_new_dishes}\n\n Теперь отправьте фото для блюда.")
    bot.register_next_step_handler(message, get_dish_photo)


@bot.message_handler(content_types=['text'],
                     func=lambda message: message.forward_from is not None and message.chat.id == admin_chat_id)
def handle_forwarded_messages(message):
    user_id = message.forward_from.id
    my_data_base.add_new_admin(user_id, "admin")
    bot.send_message(chat_id="-4102272659", text=f" Админ с id{user_id} успешно добавлен!")


@bot.message_handler(func=lambda message: message.chat.id == admin_chat_id, commands=['addAdmin'])
def handle_command_in_group(message):
    admin_id = message.from_user.id
    if admin_id==config.SUPER_ADMIN_ID:
        bot.send_message(message.chat.id, "Перешлите сообщение от юзера, которого вы хотите добавить.")
    else:
        bot.send_message(message.chat.id, "У вас недостаточно прав для выполнения этой команды ")


@bot.message_handler(func=lambda message: message.chat.id == admin_chat_id, commands=['delAdmin'])
def delete_admins(message):
     id_admins = bot.send_message(message.chat.id, "Напишите id админа которого вы хотите удалить:")
     bot.register_next_step_handler(id_admins,delete)


def delete(message):
    admin_id = message.text
    my_data_base.delete(admin_id)
    bot.send_message(chat_id=-4102272659,text="Админ был удален ")

@bot.message_handler(commands=['info'])
def info(message):
    bot.send_message(message.chat.id, f"{config.INFO_MESSAGE}")


def send_message(cur, call):
    time.sleep(cur)
    bot.send_message(call.chat.id, "Ваш заказ готов. Доставка займет 10 минут ")


def show_dishes_menu(category_key, user_id, message_id):
    markup = InlineKeyboardMarkup()
    buttons = [InlineKeyboardButton(item, callback_data='2' + item) for item in category[category_key]]

    [markup.row(buttons[i], buttons[i + 1]) for i in range(0, len(buttons) - 1, 2)]

    if len(buttons) % 2 != 0: markup.row(buttons[-1])
    markup.add(InlineKeyboardButton('В меню', callback_data='3'))
    bot.edit_message_text(chat_id=user_id, message_id=message_id, text='Выберите блюдо.', reply_markup=markup)


def show_dish_info(dish_key, chat_id):
    found_category = next((category_ for category_, dishes in category.items() if dish_key in dishes), None)

    if dish_key in info_dishes:
        dish_info_text = f"*{dish_key}*\n\n"
        dish_info_text += '\n'.join(
            [f'{list_of_list[0][n]}: {j} минут' if list_of_list[0][n] == 'Время' else
             f'{list_of_list[0][n]}: {j} BYN' if list_of_list[0][n] == 'Сумма' else
             f'{list_of_list[0][n]}: {j}' for n, j in enumerate(info_dishes[dish_key][1:], start=1)])

        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('Назад', callback_data='f' + found_category))
        markup.add(InlineKeyboardButton('Добавить в корзину', callback_data='0' + dish_key))

        if dish_key not in list(dishes_id.keys()):
            with open('/Users/mac/Downloads/Новая папка с объектами/'  + dish_key + '.jpg', 'rb') as photo:
                m = bot.send_photo(chat_id, photo=photo, caption=dish_info_text, reply_markup=markup,
                                   parse_mode='MarkdownV2')
                dishes_id[dish_key] = m.photo[-1].file_id
        else:
            bot.send_photo(chat_id, photo=dishes_id[dish_key], caption=dish_info_text,
                           reply_markup=markup)




@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id

    if user_id not in states:
        states.setdefault(user_id, {'state': None, 'shop_basket': None})

    if my_data_base.is_user_exest(user_id):
        bot.send_message(message.chat.id, "Привет!")
        states[user_id]['state'] = "начало пользования"
        states[user_id]['shop_basket'] = None
        print(states)
        handle_start(message)
    else:
        bot.send_message(message.chat.id, "Привет! Давай начнем. Введи свои данные.")
        name = bot.send_message(message.chat.id, "Введите свое имя: ")
        bot.register_next_step_handler(name, names)


def names(message):
    global user_names
    user_names = message.text
    tel = bot.send_message(message.chat.id, "Введите свой  телефон: ")
    bot.register_next_step_handler(tel, telephon)


def telephon(message):
    global tele
    tele = message.text
    ad = bot.send_message(message.chat.id, "Введите свой  адрес:")
    bot.register_next_step_handler(ad, adr)


def adr(message):
    global adres
    adres = message.text
    user_id = message.from_user.id
    my_data_base.insert_user_data(user_id, user_names, tele, adres)
    bot.send_message(message.chat.id, "Данные будут успешно добавлены ")



@bot.message_handler(func=lambda message: message.chat.id == admin_chat_id, commands=['show_users'])
def bd(message):
        con = sl.connect("vk_tg1.db")
        user = con.execute("SELECT * FROM Users")
        for d in user.fetchall():
            bot.send_message(message.chat.id, "_________________________")
            bot.send_message(message.chat.id, f"ID:{d[1]}")
            bot.send_message(message.chat.id, f"Имя:{d[2]}")
            bot.send_message(message.chat.id, f"Номер:{d[3]}")


@bot.message_handler(commands=['menu'])
def handle_start(message):
    user_id = message.from_user.id
    if my_data_base.is_user_exest(user_id):
        bot.send_message(message.chat.id, "Выберите категорию блюда ⬇️", reply_markup=markupI)
        states[user_id]['state'] = "пользователь в меню"
        states[user_id]['shop_basket'] = states[user_id].get('shop_basket', {})
        print(states)
    else:

        bot.send_message(message.chat.id, "Вы не зарегистрированы! Нажмите /start и пройдите регистрацию.")
@bot.message_handler(commands=['shop_bag'])
def shopping_bag(message):
    user_id = message.from_user.id
    if my_data_base.is_user_exest(user_id):
        user_shop_basket = states[user_id].get('shop_basket', {})  # Используем user_shop_basket вместо shop_bag
        if not user_shop_basket:
            states[user_id]['state'] = "Пользователь в корзине"
            states[user_id]['shop_basket'] = None
            response = "Ваша корзина пуста."
            bot.send_message(message.chat.id, response, reply_markup=markup)
        else:
            response = '\n'.join(
                [f'{item} [x{details[2]}] = {int(details[1]) * int(details[2])} BYN' for item, details in
                 user_shop_basket.items()])
            states[user_id]['state'] = "Пользователь в корзине"
            states[user_id]['shop_basket'] = user_shop_basket
            markupShop_Bag = InlineKeyboardMarkup().row(
                InlineKeyboardButton('Очистить корзину', callback_data='clear'),
                InlineKeyboardButton('Изменить корзину', callback_data='change')).row(
                InlineKeyboardButton('Оформить заказ', callback_data='order'))

            bot.send_message(message.chat.id, response, reply_markup=markupShop_Bag)
    else:
        bot.send_message(message.chat.id, "Вы не зарегистрированы! Нажмите /start и пройдите регистрацию.")


@bot.message_handler(commands=['show_all_admins'])
def show_all_admins(message):
    user_id = message.from_user.id
    if my_data_base.is_admin_exest(user_id):
        con = sl.connect("vk_tg1.db")
        user = con.execute("SELECT * FROM ADMIN")

        for d in user.fetchall():
            user_id = d[1]
            try:
                user_info = bot.get_chat_member(message.chat.id, user_id)
                username = user_info.user.username
                status = d[2]
                bot.send_message(message.chat.id, f"Username: @{username}, Статус: {status}")
            except:
                bot.send_message(message.chat.id, f"ID админа : {user_id}")
    else:
        bot.send_message(message.chat.id, "Извините , у вас не прав администратора ")


@bot.message_handler(commands=["show_my_order"])
def show_orders(message):
    user_id = message.from_user.id
    if my_data_base.is_user_exest(user_id):
        result = my_data_base.get_order(user_id)
        bot.send_message(message.chat.id, f"_____________________\nВаш заказ: {result}\n_____________________")
    else:
        bot.send_message(message.chat.id, "Вы не зарегистрированы! Нажмите /start и пройдите регистрацию.")


@bot.message_handler(commands=["help"])
def help(message):
    user_id = message.from_user.id
    if my_data_base.is_user_exest(user_id):
        user_name = message.from_user.username or message.from_user.first_name or message.from_user.last_name
        bot.send_message(chat_id="-4102272659", text=f" @{user_name} нужна помощь ")
    else:
        bot.send_message(message.chat.id, "Вы не зарегистрированы!\nНажмите /start и пройдите регистрацию")


print("Running")
bot.polling(none_stop=True)
