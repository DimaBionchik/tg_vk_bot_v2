import telebot
import config
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3 as sl
import my_data_base
import gspread


bot = telebot.TeleBot(config.TOKEN)
states = {}
gs = gspread.service_account(filename="my-test-project-408312-296aa9c49a83.json")
ADMIN_ID =['718611792','626220085']
sh_connection = gs.open_by_url(
    "https://docs.google.com/spreadsheets/d/1qvu3Wn0RXy3WyyetWimApzzTARtfQwNaajcnowmTdyw/edit#gid=0")
worksheet = sh_connection.sheet1
list_of_list = worksheet.get_all_values()
category = {}
info_dishes = {}
shop_bag = {}

# Словарь с категориями и продуктами (category)
for i in list_of_list[1:]:
    category.setdefault(i[4], []).append(i[1])

# Словарь с продуктами и их описанием (info_dishes)
for name in list_of_list[1:]:
    info_dishes[name[1]] = [name[0], name[2], name[3]]

print(category)
print(info_dishes)

# Главная клавиатура
markupI = InlineKeyboardMarkup()
for name in category.keys():
    markupI.add(InlineKeyboardButton(name, callback_data=name))

markup = InlineKeyboardMarkup()
markup.add(InlineKeyboardButton('В меню', callback_data='3'))

@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    if call.data in category:
        message_id = call.message.message_id
        show_dishes_menu(call.data, call.from_user.id, message_id)

    elif call.data[0] == '3':
        handle_start(call.message)

    elif call.data[0] == '2':
        show_dish_info(call.data[1:], call.message.chat.id)

    elif call.data[0] == '0':
        add_to_shop_bag(call.data[1:])

def add_to_shop_bag(data):
    shop_bag[data] = info_dishes[data][1:]
    print(shop_bag)

def show_dishes_menu(category_key, user_id, message_id):
    markup = InlineKeyboardMarkup()
    for item in category[category_key]:
        markup.add(InlineKeyboardButton(item, callback_data='2' + item))
    markup.add(InlineKeyboardButton('В меню', callback_data='3'))
    bot.edit_message_reply_markup(chat_id=user_id, message_id=message_id, reply_markup=markup)


def show_dish_info(dish_key, chat_id):
    found_category = next((category_ for category_, dishes in category.items() if dish_key in dishes), None)

    if dish_key in info_dishes:
        dish_info_text = f"{dish_key}\n"
        dish_info_text += '\n'.join(
            [f'{list_of_list[0][n + 1]}: {j}' for n, j in enumerate(info_dishes[dish_key][1:], start=1)])
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('В меню', callback_data='3'))
        markup.add(InlineKeyboardButton('Назад', callback_data=found_category))
        markup.add(InlineKeyboardButton('Добавить в корзину', callback_data='0' + dish_key))
        bot.send_message(chat_id, dish_info_text, reply_markup=markup)


@bot.message_handler(commands=['list_admins'])
def list_admins(message):
    us_id = message.from_user.id

    # Проверка, является ли отправитель администратором
    if str(us_id) in config.ADMIN_ID:
        admins_list = "\n".join([str(admin_id) for admin_id in config.ADMIN_ID])
        bot.send_message(message.chat.id, f"Список администраторов:\n{admins_list}")
    else:
      pass


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if my_data_base.is_user_exest(user_id):
        bot.send_message(message.chat.id, "Привет! Ты уже зарегистрирован.")
    else:

        bot.send_message(message.chat.id, "Привет! Давай начнем. Введи свои данные.")
        name = bot.send_message(message.chat.id, "Введите свое имя: ")
        bot.register_next_step_handler(name, names)

def names(message):
    global user_names
    user_names = message.text
    tel = bot.send_message(message.chat.id,"Введите свой  телефон: ")
    bot.register_next_step_handler(tel,telephon)

def telephon(message):
    global tele
    tele = message.text
    ad = bot.send_message(message.chat.id,"Введите свой  адрес:")
    bot.register_next_step_handler(ad, adr)


def adr(message):
    global adres
    adres = message.text
    user_id = message.from_user.id
    insert_user_data(user_id,user_names,tele,adres)
    bot.send_message(message.chat.id, "Данные будут успешно добавлены ")



def insert_user_data( user_id, user_name, user_tel, user_address):
    con = sl.connect("vk_tg1.db")
    with con:
        con.execute("""
            INSERT INTO Users (tg_id, name, tel, adress) 
            VALUES (?, ?, ?, ?);
        """, (str(user_id), user_name, user_tel, user_address))

@bot.message_handler(commands=['show_user'])
def bd(message):
    con = sl.connect("vk_tg1.db")
    user = con.execute("SELECT * FROM Users")
    for d in user.fetchall():
        bot.send_message(message.chat.id, "_________________________")
        bot.send_message(message.chat.id,f"ID:{d[1]}")
        bot.send_message(message.chat.id, f"Имя:{d[2]}")
        bot.send_message(message.chat.id, f"Номер:{d[3]}")
        bot.send_message(message.chat.id, "_________________________")


@bot.message_handler(commands=['admin'])
def admin(message):
    bot.send_message(message.chat.id, "Ожидайте")
    us_id =message.from_user.id
    print(us_id)
    if str(us_id) in  config.ADMIN_ID:
        bot.send_message(message.chat.id,"ты админ ")
    else:
        bot.send_message(message.chat.id, "у тебя нет прав  ")



@bot.message_handler(commands=['menu'])
def handle_start(message):
    bot.send_message(message.chat.id, "Выберите категорию блюда ⬇️", reply_markup=markupI)



@bot.message_handler(commands=['shop_bag'])
def shopping_bag(message):
    response = "Ваша корзина пуста." if not shop_bag else "В корзине есть продукты."
    bot.send_message(message.chat.id, response, reply_markup=markup)


@bot.message_handler(commands=['show_all_admins'])
def show_all_admins(message):
    bot.send_message(message.chat.id,"Ожидайте , выполняется запрос в БД" )
    con = sl.connect("vk_tg1.db")
    user = con.execute("SELECT * FROM ADMIN")
    for d in user.fetchall():
        bot.send_message(message.chat.id, "_________________________")
        bot.send_message(message.chat.id, f"ID:{d[1]}")
        bot.send_message(message.chat.id, f"Статус:{d[2]}")
        bot.send_message(message.chat.id,"_________________________")



@bot.message_handler(commands=["help"])
def help(message):
    user_id = message.from_user.id
    bot.send_message(chat_id="-4102272659", text=f"{user_id} требует помощи ")

print("e")
bot.polling(none_stop=True)