import telebot
import config
import gspread

# TOKEN = '6785210916:AAHUs04JflhGVqjgmkxCoV4RFqxfs7EJSfE'
bot = telebot.TeleBot(config.TOKEN)
gs = gspread.service_account(filename="my-test-project-408312-296aa9c49a83.json")
sh_connection = gs.open_by_url("https://docs.google.com/spreadsheets/d/1qvu3Wn0RXy3WyyetWimApzzTARtfQwNaajcnowmTdyw/edit#gid=0")
worksheet = sh_connection.sheet1
list_of_list = worksheet.get_all_values()
print(list_of_list)
category  =[]
name_dishes = []
time =[]
price =[]
for cat in list_of_list[1:]:category.append(cat[4])
for name in list_of_list[1:]:name_dishes.append(name[1])
for times in list_of_list[1:]:time.append(times[2])
for prices in list_of_list[1:]:price.append(prices[3])
print(name_dishes)
print(time)
print(price)
print(category)
ADMIN_ID ="718611792"



@bot.message_handler(commands=['start'])
def start(message):


    bot.send_message(message.chat.id,"hello")


@bot.message_handler(commands=['admin'])
def admin(message):
    bot.send_message(message.chat.id, "Ожидайте")
    us_id =message.from_user.id
    print(us_id)
    if str(us_id) == ADMIN_ID:
        bot.send_message(message.chat.id,"ты админ ")
    else:
        bot.send_message(message.chat.id, "у тебя нет прав  ")







print("e")
bot.polling(none_stop=True)