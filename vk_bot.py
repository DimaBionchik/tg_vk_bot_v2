import config

import sqlite3 as sl
import my_data_base
import gspread
from google.oauth2 import service_account
import time
import requests
from vk_api import VkApi, longpoll, keyboard
from vk_api.utils import get_random_id
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import json
import gspread

GROUP_ID = config.GROUP_ID_VK
GROUP_TOKEN = config.GROUP_TOKEN_VK
API_VERSION = config.API_VERSION_VK

vk_session = VkApi(token=GROUP_TOKEN, api_version=API_VERSION)
vk = vk_session.get_api()
longpol = VkBotLongPoll(vk_session, group_id=GROUP_ID)

gs = gspread.service_account(filename=config.JSON_FILE)
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = service_account.Credentials.from_service_account_file("my-test-project-408312-296aa9c49a83.json", scopes=scope)
client = gspread.authorize(creds)
spreadsheet_url = config.GOOGLE
sheet = client.open_by_url(spreadsheet_url).sheet1
sh_connection = gs.open_by_url(config.GOOGLE)
worksheet = sh_connection.sheet1
list_of_list = worksheet.get_all_values()

category = {}
info_dishes = {}
info_new_dishes = []
shop_bag = {}
dishes_id = {}
states = {}
user_data = {}
gl_resp = ""
for name in list_of_list[1:]:
    info_dishes[name[0]] = [True, name[1], name[2]]

for i in list_of_list[1:]:
    if info_dishes[i[0]][0] is True:
        category.setdefault(i[3], []).append(i[0])

amount = 0
amounts = 0
MAX_CATEGORIES_ON_PAGE = 2
g
klava = VkKeyboard(one_time=False, inline=True)
klava.add_callback_button(label="Да",color=VkKeyboardColor.SECONDARY,payload={"type":"da"})
klava.add_callback_button(label="Нет",color=VkKeyboardColor.SECONDARY,payload={"type":"net"})
def upload_photo(peer_id, dish_key):
    upload_url = vk.photos.getMessagesUploadServer(peer_id=peer_id)['upload_url']

    with open('/Users/mac/Downloads/Новая папка с объектами/' + dish_key + '.jpg', 'rb') as photo:
        files = {'photo': photo}
        response = requests.post(upload_url, files=files)
        data = response.json()

    saved_photo = vk.photos.saveMessagesPhoto(
        photo=data['photo'],
        server=data['server'],
        hash=data['hash'])[0]

    return saved_photo['owner_id'], saved_photo['id']
def gen_board(labels):
    global amount
    keyboard = VkKeyboard(one_time=False, inline=True)
    start_idx = amount * MAX_CATEGORIES_ON_PAGE
    end_idx = min((amount + 1) * MAX_CATEGORIES_ON_PAGE, len(labels))

    for i in range(start_idx, end_idx, 2):
        label1 = labels[i]
        keyboard.add_callback_button(label=label1, color=VkKeyboardColor.SECONDARY,
                                     payload={"type": "text", "category_name": label1})

        if i + 1 < end_idx:
            label2 = labels[i + 1]
            keyboard.add_callback_button(label=label2, color=VkKeyboardColor.SECONDARY,
                                         payload={"type": "text", "category_name": label2})

        keyboard.add_line()

    if amount > 0:
        keyboard.add_callback_button(label='Назад', color=VkKeyboardColor.PRIMARY, payload={"type": "Назад"})
    if end_idx < len(labels):
        keyboard.add_callback_button(label='Далее', color=VkKeyboardColor.PRIMARY, payload={"type": "Далее"})

    return keyboard

def gen_board_dishes(labels,category_name):
    global amounts

    keyboards = VkKeyboard(one_time=False, inline=True)
    start_idx = amounts * MAX_CATEGORIES_ON_PAGE
    end_idx = min((amounts + 1) * MAX_CATEGORIES_ON_PAGE, len(labels))

    for i in range(start_idx, end_idx, 2):
        label1 = labels[i]
        keyboards.add_callback_button(label=label1, color=VkKeyboardColor.SECONDARY,
                                     payload={"type": "dishes_name", "dishes_names": label1})

        if i + 1 < end_idx:
            label2 = labels[i + 1]
            keyboards.add_callback_button(label=label2, color=VkKeyboardColor.SECONDARY,
                                         payload={"type": "dishes_name", "dishes_names": label2})

        keyboards.add_line()

    if amounts > 0:
        keyboards.add_callback_button(label='Вернуться', color=VkKeyboardColor.PRIMARY, payload={"type": "Вернуться",  "dishes_name": category_name})
    if end_idx < len(labels):
        keyboards.add_callback_button(label='Вперед', color=VkKeyboardColor.PRIMARY,payload={"type": "Вперед", "dishes_name": category_name})
    keyboards.add_callback_button(label='В меню', color=VkKeyboardColor.PRIMARY,
                 payload={"type": "В меню"})

    return keyboards

def start(event):
    user_id = event.obj.message['from_id']

    if user_id not in states:
        states[user_id] = {'state': None, 'shop_basket': None}

    if my_data_base.is_user_exest(user_id):
        send_message(user_id=user_id, keyboard=gen_board(list(category.keys())).get_keyboard(), text='Выберите категорию.')
        states[user_id]['state'] = "Начало пользования."
        states[user_id]['shop_basket'] = None
    else:
        send_message(user_id, keyboard=None, text='Привет! Давай начнем. Введи свои данные.')
        states[user_id]['state'] = "Ожидание_имени"
    print(states)

def process_message(event):
    user_id = event.obj.message['from_id']

    if user_id not in user_data:
        user_data[user_id] = {'name': None, 'phone': None, 'address': None}

    if user_id not in states:
        states[user_id] = {'state': None, 'shop_basket': None}

    if user_id in states:
        current_state = states[user_id]['state']

        if current_state == "Ожидание_имени":
            user_data[user_id]['name'] = event.obj.message['text']
            states[user_id]['state'] = "Ожидание_телефона"
            send_message(user_id, keyboard=None, text='Введите свой телефон: ')
        elif current_state == "Ожидание_телефона":
            user_data[user_id]['phone'] = event.obj.message['text']
            states[user_id]['state'] = "Ожидание_адреса"
            send_message(user_id, keyboard=None, text='Введите свой адрес: ')
        elif current_state == "Ожидание_адреса":
            user_data[user_id]['address'] = event.obj.message['text']
            my_data_base.insert_user_data(user_id, user_data[user_id]['name'], user_data[user_id]['phone'],
                                          user_data[user_id]['address'])
            send_message(user_id, keyboard=None, text='Данные успешно добавлены')
    print(states)



def get_keyboard(is_true = False,resp = None):
    if is_true == False:
        keyboard_one = VkKeyboard(one_time=False, inline=True)
        keyboard_one.add_callback_button(label='В меню', color=VkKeyboardColor.PRIMARY,payload={"type": "В меню"})
        keyboard_one.add_callback_button(label="В корзину",color=VkKeyboardColor.PRIMARY,payload={'type':"shop_bag"})
    else:
        keyboard_one = VkKeyboard(one_time=False, inline=True)
        keyboard_one.add_callback_button(label='В меню', color=VkKeyboardColor.PRIMARY, payload={"type": "В меню"})
        keyboard_one.add_callback_button(label="Оформить заказ", color=VkKeyboardColor.PRIMARY, payload={'type': "Order",'resonc':resp})
    return keyboard_one



def show_dish_info(dish_key, peer_id):

    if dish_key in info_dishes:
        dish_info_text = f"{dish_key}.\n\n"
        dish_info_text += '\n'.join(
            [f'{list_of_list[0][n]}: {j} минут' if list_of_list[0][n] == 'Время' else
             f'{list_of_list[0][n]}: {j} BYN' if list_of_list[0][n] == 'Сумма' else
             f'{list_of_list[0][n]}: {j}' for n, j in enumerate(info_dishes[dish_key][1:], start=1)])

        owner_id, photo_id = upload_photo(peer_id, dish_key)


        keyboard = VkKeyboard(one_time=False, inline=True)
        keyboard.add_callback_button(label="Добавить в корзину", color=VkKeyboardColor.PRIMARY, payload={"type": "add", "object": dish_key})
        keyboard.add_callback_button(label="В меню", color=VkKeyboardColor.PRIMARY, payload={"type": "В меню"})

        vk.messages.edit(
            peer_id=peer_id,
            message=dish_info_text,
            attachment=f'photo{owner_id}_{photo_id}',
            keyboard=keyboard.get_keyboard(),
            conversation_message_id=event.obj.conversation_message_id
        )

def send_message(user_id, keyboard, text):
    vk.messages.send(user_id=user_id, random_id=get_random_id(), keyboard=keyboard, message=text)


print('Running..')

for event in longpol.listen():

    if event.type == VkBotEventType.MESSAGE_NEW and event.from_user:
        if event.obj.message.get('text') == '/start':
            start(event)

        elif event.obj.message.get('text') == '/shop_bag':
            user_id = event.obj.message['from_id']
            print(f"user id = {user_id}")
            states_shop_basket = states[user_id]['shop_basket']
            if states_shop_basket:
                response = '\n'.join(
                    [f'{item} [x{details[-1]}] = {int(details[2]) * int(details[-1])} BYN.' for item, details in
                     states_shop_basket.items()])
                cur = max(int(info_dishes[i][1]) for i in states_shop_basket) if states_shop_basket else 0
                response += f'\nПримерное время доставки: {cur + 10} минут.'
                states[user_id]['state'] = "юзер в корзине"
                states[user_id]['shop_basket'] = states_shop_basket
                print(states)

                send_message(user_id, keyboard=None, text=response)

        elif states[event.obj.message['from_id']]['state'] == "Ожидание_отзыва":
            user_id = event.obj.message['from_id']
            feedback_text = event.obj.message.get('text')
            basket = states[user_id]['shop_basket']
            my_data_base.insert_into_disches_answer(response,user_id,feedback_text)
            send_message(event.obj.message['from_id'], None, "Спасибо за отзыв!")
            states[event.obj.message['from_id']]['state'] = None

        else:
            process_message(event)


    elif event.type == VkBotEventType.MESSAGE_EVENT:

        if event.object.payload.get('type') in ('show_snackbar', 'open_link', 'open_app'):
            vk.messages.sendMessageEventAnswer(event_id=event.object.event_id,user_id=event.object.user_id,
                peer_id=event.object.peer_id,
                event_data=json.dumps(event.object.payload))

        elif event.object.payload.get('type') == "Далее":
            amount += 1
            vk.messages.edit(peer_id=event.obj.peer_id, message='Выберите категорию.',conversation_message_id=event.obj.conversation_message_id,
                keyboard=gen_board(list(category.keys())).get_keyboard())

        elif event.object.payload.get('type') == "Назад" and amount > 0:
            amount -= 1
            vk.messages.edit(
                peer_id=event.obj.peer_id,
                message='Выберите категорию.',
                conversation_message_id=event.obj.conversation_message_id,
                keyboard=gen_board(list(category.keys())).get_keyboard())

        elif event.object.payload.get('type') == "Вперед":
            category_name = event.object.payload.get('dishes_name')
            amounts += 1
            if category_name:
                vk.messages.edit(
                    peer_id=event.obj.peer_id,
                    message='Выберите блюда:',
                    conversation_message_id=event.obj.conversation_message_id,
                    keyboard=gen_board_dishes(list(category[category_name]),category_name=category_name).get_keyboard()
                )

        elif event.object.payload.get('type') == "Вернуться" and amounts > 0:
            category_name = event.object.payload.get('dishes_name')
            amounts -= 1
            if category_name:
                vk.messages.edit(
                    peer_id=event.obj.peer_id,
                    message='Выберите блюда:',
                    conversation_message_id=event.obj.conversation_message_id,
                    keyboard=gen_board_dishes(list(category[category_name]),category_name=category_name).get_keyboard())

        elif event.object.payload.get('type') == "text":
            category_name = event.object.payload.get('category_name')
            if category_name:
                vk.messages.edit(
                    peer_id=event.obj.peer_id,
                    message='Выберите блюда:',
                    conversation_message_id=event.obj.conversation_message_id,
                    keyboard=gen_board_dishes(list(category[category_name]), category_name=category_name).get_keyboard())

        elif event.object.payload.get('type') == "В меню":
            vk.messages.edit(
                peer_id=event.obj.peer_id,
                message='Выберите категорию.',
                conversation_message_id=event.obj.conversation_message_id,
                keyboard=gen_board(list(category.keys())).get_keyboard())

        elif event.object.payload.get('type') == "dishes_name":
            dis_name = event.object.payload.get('dishes_names')
            if dis_name:
               show_dish_info(dis_name,peer_id=event.obj.peer_id)

        elif event.object.payload.get('type') == "dishes_name":
            dis_name = event.object.payload.get('dishes_names')
            if dis_name:
               show_dish_info(dis_name,peer_id=event.obj.peer_id)

        elif event.object.payload.get('type') == "add":
            user_id = event.obj.user_id
            dish_name = event.object.payload.get('object')
            states[user_id]['shop_basket'] = {dish_name: info_dishes[dish_name] + [0]}
            states[user_id]['shop_basket'][dish_name][-1] += 1
            states[user_id]['state'] = "Добавление товара."
            vk.messages.edit(
                peer_id=event.obj.peer_id,
                message='Товар успешно добавлен.',
                conversation_message_id=event.obj.conversation_message_id,
                keyboard=get_keyboard(is_true=False).get_keyboard())

        elif event.object.payload.get('type') == "shop_bag":
            user_id = event.obj.user_id
            states_shop_basket = states[user_id]['shop_basket']

            if states_shop_basket:
                response = '\n'.join(
                    [f'{item} [x{details[3]}] = {int(details[1]) * int(details[3])} BYN.' for item, details in
                     states_shop_basket.items()])
                cur = max(int(info_dishes[i][1]) for i in states_shop_basket) if states_shop_basket else 0
                response += f'\nПримерное время доставки: {cur + 10} минут.'
                states[user_id]['state'] = "юзер в корзине"
                states[user_id]['shop_basket'] = states_shop_basket
                print(states)
                vk.messages.edit(
                    peer_id=event.obj.peer_id,
                    message=response,
                    conversation_message_id=event.obj.conversation_message_id,
                    keyboard=get_keyboard(is_true=True,resp = response).get_keyboard())

        elif event.object.payload.get('type') == "Order":
            user_id = event.obj.user_id
            category_name = event.object.payload.get('responc')
            price, count = 0, 0
            states_shop_basket = states[user_id]['shop_basket']

            for dish, details in states_shop_basket.items():
                name_dishes = dish
                price = price + int(details[1])
                counts = details[2]
                my_data_base.upd(name_dishes, counts)
            count += 1
            response = '\n'.join(
                [f'{item} [x{details[3]}] = {int(details[1]) * int(details[3])} BYN.' for item, details in
                 states_shop_basket.items()])

            states[user_id]['state'] = "Оформление заказа"
            states[user_id]['shop_basket'] = states_shop_basket
            print(states)

            gl_resp = category_name
            cur = max(int(info_dishes[i][1]) for i in states_shop_basket) if states_shop_basket else 0
            response += f'\nПримерное время доставки: {cur + 10} минут.'
            print(states_shop_basket)
            my_data_base.upd_user(user_id, states_shop_basket)

            message = my_data_base.check_dishes()
            vk.messages.edit(
                peer_id=event.obj.peer_id,
                message=f"Ваш заказ №{count}\n____________________\n\nСостав заказа:\n{response}\n\nКонечная стоимость: {price} BYN.",
                conversation_message_id=event.obj.conversation_message_id,
                keyboard=None)

            states_shop_basket.clear()
            states[user_id]['shop_basket'] = None
            send_message(user_id,klava.get_keyboard() ,"Хотите оставить отзыв?")
            states[user_id]['state'] = "Заказ оформлен"

        elif event.object.payload.get('type') == "da":
            user_id = event.obj.user_id
            send_message(user_id,None,"Напишите отзыв:")
            states[user_id]['state'] = "Ожидание_отзыва"
        elif event.object.payload.get('type') == "net":
            user_id = event.obj.user_id
            vk.messages.edit(
                peer_id=event.obj.peer_id,
                message="Спасибо за заказ, ожидайте!Для нового заказа введите /start",
                conversation_message_id=event.obj.conversation_message_id,
                keyboard=None)

