import telebot
import config
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3 as sl
import my_data_base
import gspread
import time


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


for i in list_of_list[1:]:
    category.setdefault(i[4], []).append(i[1])


for name in list_of_list[1:]:
    info_dishes[name[1]] = [name[0], name[2], name[3]]


markupANS =InlineKeyboardMarkup()
markupANS.add(InlineKeyboardButton("да",callback_data="yes"))
markupANS.add(InlineKeyboardButton("Нет",callback_data="no"))
markupI = InlineKeyboardMarkup()
for name in category.keys():
    markupI.add(InlineKeyboardButton(name, callback_data=name))

markup = InlineKeyboardMarkup()
markup.add(InlineKeyboardButton('В меню', callback_data='3'))
@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    user_id = call.from_user.id

    if call.data in category:
        message_id = call.message.message_id
        show_dishes_menu(call.data, call.from_user.id, message_id)

    elif call.data[0] == '3':
        handle_start(call.message)

    elif call.data[0] == '2':
        show_dish_info(call.data[1:], call.message.chat.id)

    elif call.data[0] == '0':
        add_to_shop_bag(call.data[1:], call.from_user.id)

    elif call.data == 'shop_bag':
        if shop_bag:
            response = '\n'.join(
                [f'{item} [x{details[2]}] = {int(details[1]) * int(details[2])} BYN.' for item, details in
                 shop_bag.items()])
            cur = max(int(info_dishes[i][1]) for i in shop_bag) if shop_bag else 0
            response += f'\nПримерное время доставки : {cur + 10} минут.'
            markupG = InlineKeyboardMarkup()
            markupG.add(InlineKeyboardButton('Изменить корзину', callback_data='change'))
            markupG.add(InlineKeyboardButton('Очистить корзину', callback_data='clear'))
            markupG.add(InlineKeyboardButton("Оформить заказ",callback_data="order"))
            bot.send_message(call.message.chat.id, response, reply_markup=markupG)
        else:
            bot.send_message(call.message.chat.id, 'Корзина пуста.', reply_markup=markup)

    elif call.data == 'clear':
        shop_bag.clear()
        bot.send_message(call.message.chat.id, 'Корзина пуста.', reply_markup=markup)
    elif call.data =="yes":
        answer = bot.send_message(call.message.chat.id,"Напишите свой отзыв(не больше 300 символов):")
        bot.send_message(call.message.chat.id,"Cпасибо за отзыв, если хотите продолжить жмите /menu")
        bot.register_next_step_handler(answer,answers)

    elif call.data =='no':
        bot.send_message(call.message.chat.id,'Спасибо за заказ!Будем ждать вас еще!')
    elif call.data == "order":
        price = 0
        count = 0
        print(shop_bag)
        for dish, details in shop_bag.items():
            name_dishes = dish
            price =price+ int(details[1])
            counts = details[2]
            my_data_base.upd(name_dishes, counts)
        count += 1
        response = '\n'.join(
            [f'{item} [x{details[2]}] = {int(details[1]) * int(details[2])} BYN.' for item, details in
             shop_bag.items()])
        cur = max(int(info_dishes[i][1]) for i in shop_bag) if shop_bag else 0
        response += f'\nПримерное время доставки : {cur + 10} минут.'
        my_data_base.upd_user(user_id,shop_bag)
        bot.send_message(chat_id="-4102272659", text=f" Пользователь({user_id}), оформил заказ :{response} ")
        message = my_data_base.check_dishes()
        bot.send_message(chat_id="-4102272659", text=f" {message} ",reply_markup=markupI)
        bot.send_message(call.message.chat.id,f"Ваш заказ №{count}")
        bot.send_message(call.message.chat.id, "____________________")
        bot.send_message(call.message.chat.id,f"Состав заказа : {response}")
        bot.send_message(call.message.chat.id,f"Конечная стоимость:{price} ")
        shop_bag.clear()
        # send_message(cur, call.message)
        bot.send_message(call.message.chat.id,"Хотите оставить отзыв?",reply_markup=markupANS)

    for operation in ['-', '+', 'd']:
        if call.data.startswith(operation) and call.data[1:] in shop_bag:
            if operation in ['-', '+']:
                shop_bag[call.data[1:]][2] = str(int(shop_bag[call.data[1:]][2]) + (1 if operation == '+' else -1))
                total_cost = int(shop_bag[call.data[1:]][1]) * int(shop_bag[call.data[1:]][2])
                dish_info_text = f'Стоимость = {total_cost} BYN.\nКоличество = {shop_bag[call.data[1:]][2]}.'
                with open(f'/Users/mac/Downloads/Новая папка с объектами/{call.data[1:]}.jpg', 'rb') as photo:
                    markupG = InlineKeyboardMarkup()
                    markupG.add(InlineKeyboardButton('-', callback_data=f'-{call.data[1:]}'))
                    markupG.add(InlineKeyboardButton('Удалить продукт.', callback_data=f'delete{call.data[1:]}'))
                    markupG.add(InlineKeyboardButton('+', callback_data=f'+{call.data[1:]}'))
                    bot.send_photo(call.from_user.id, photo=photo, caption=dish_info_text, reply_markup=markupG)
            elif operation == 'd':
                del shop_bag[call.data[1:]]
                bot.send_message(call.message.chat.id, 'Товар успешно удален.', reply_markup=markup)

def answers(message):
    ans = message.text

    print(ans)
@bot.message_handler(commands=['info'])
def info(message):
    bot.send_message(message.chat.id,f"{config.INFO_MESSAGE}")

def send_message(cur,call):
    time.sleep(cur)
    bot.send_message(call.chat.id,"Ваш заказ готов,доставка займет 10 минут ")

def add_to_shop_bag(data, chat_id):
    shop_bag[data] = shop_bag.get(data, info_dishes[data][1:] + [0])
    shop_bag[data][-1] += 1
    markupI = InlineKeyboardMarkup()
    markupI.add(InlineKeyboardButton('В меню', callback_data='3'))
    markupI.add(InlineKeyboardButton('Просмотр корзины', callback_data='shop_bag'))
    bot.send_message(chat_id, 'Товар успешно добавлен.', reply_markup=markupI)


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
        with open('/Users/mac/Downloads/Новая папка с объектами/' + dish_key + '.jpg', 'rb') as photo:
            bot.send_photo(chat_id, photo=photo, caption=dish_info_text, reply_markup=markup)



@bot.message_handler(commands=['list_admins'])
def list_admins(message):
    us_id = message.from_user.id

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
        states[user_id] = 'начало'
        print(states)
        handle_start(message)
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
    my_data_base.insert_user_data(user_id,user_names,tele,adres)
    bot.send_message(message.chat.id, "Данные будут успешно добавлены ")
    states[user_id] = 'начало'
    print(states)




@bot.message_handler(commands=['show_user'])
def bd(message):
    con = sl.connect("vk_tg1.db")
    user = con.execute("SELECT * FROM Users")
    for d in user.fetchall():
        bot.send_message(message.chat.id, "_________________________")
        bot.send_message(message.chat.id,f"ID:{d[1]}")
        bot.send_message(message.chat.id, f"Имя:{d[2]}")
        bot.send_message(message.chat.id, f"Номер:{d[3]}")



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
    user_id = message.from_user.id

    bot.send_message(message.chat.id, "Выберите категорию блюда ⬇️", reply_markup=markupI)
    states[user_id] = 'пользователь в меню '
    print(states)
# else:
    #     bot.send_message(message.chat.id,"Вы не зарегистрированы!  Нажмите /start  и пройдите регистрацию")


@bot.message_handler(commands=['shop_bag'])
def shopping_bag(message):
    user_id = message.from_user.id
    if my_data_base.is_user_exest(user_id):
        if not shop_bag:
            states[user_id] = "юзер в корзине "
            print(states)
            response = "Ваша корзина пуста."
            bot.send_message(message.chat.id, response, reply_markup=markup)
        else:
            response = '\n'.join(
                [f'{item} [x{details[2]}] = {int(details[1]) * int(details[2])} BYN' for item, details in shop_bag.items()])
            markup.add(InlineKeyboardButton('Изменить корзину', callback_data='change'))
            markup.add(InlineKeyboardButton('Очистить корзину', callback_data='clear'))
            markup.add(InlineKeyboardButton('Оформить заказ', callback_data='order'))
            bot.send_message(message.chat.id, response, reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Вы не зарегистрированы!  Нажмите /start и пройдите регистрацию")


@bot.message_handler(commands=['show_all_admins'])
def show_all_admins(message):
    bot.send_message(message.chat.id,"Ожидайте , выполняется запрос в БД" )
    con = sl.connect("vk_tg1.db")
    user = con.execute("SELECT * FROM ADMIN")
    for d in user.fetchall():
        bot.send_message(message.chat.id, "_________________________")
        bot.send_message(message.chat.id, f"ID:{d[1]}")
        bot.send_message(message.chat.id, f"Статус:{d[2]}")





@bot.message_handler(commands=["show_my_order"])
def show_orders(message):
    user_id = message.from_user.id
    result = my_data_base.get_order(user_id)
    bot.send_message(message.chat.id,"_____________________")
    bot.send_message(message.chat.id,f"Ваш заказ {result}")
    bot.send_message(message.chat.id, "_____________________")

@bot.message_handler(commands=["help"])
def help(message):
    user_id = message.from_user.id
    if my_data_base.is_user_exest(user_id):
        user_name = message.from_user.username or message.from_user.first_name or message.from_user.last_name
        bot.send_message(chat_id="-4102272659", text=f" @{user_name} нужна помощь ")
    else:
        bot.send_message(message.chat.id, "Вы не зарегистрированы!  Нажмите /start и пройдите регистрацию")


print("e")
bot.polling(none_stop=True)