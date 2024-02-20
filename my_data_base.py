import sqlite3 as sl

con = sl.connect("vk_tg1.db")


def create_con(con):
    with con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS Users(
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            tg_id VARCHAR,
            name VARCHAR,
            tel VARCHAR,
            adress VARCHAR);
            """)
        con.execute("""
            CREATE TABLE IF NOT EXISTS ADMIN(
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            tg_id VARCHAR,
            status VARCHAR);""")




def insert_user_data( user_id, user_name, user_tel, user_address):
    con = sl.connect("vk_tg1.db")
    with con:
        con.execute("""
            INSERT INTO Users (tg_id, name, tel, adress) 
            VALUES (?, ?, ?, ?);
        """, (str(user_id), user_name, user_tel, user_address))

def format_basket_item(name, item):
    time, price_per_unit, quantity = map(int, item)
    total_price = quantity * price_per_unit
    return f"{name}: {quantity} шт., {price_per_unit} цена/шт., {time} время, {total_price} цена"

def upd_user(user_id,baskets):
    con = sl.connect("vk_tg1.db")
    with con:
        formatted_basket = '; '.join([format_basket_item(name, item) for name, item in baskets.items()])
        con.execute(f"""
            UPDATE Users
            SET BASKET = '{formatted_basket}'
            WHERE tg_id = {user_id}
            """)

def upd(name_dishes, counts):
    con = sl.connect("vk_tg1.db")
    with con:
        con.execute(f"""
        UPDATE Dishes
        SET count = count - {counts}
        WHERE name_dishes = '{name_dishes}'
        """)



def check_dishes():
    con = sl.connect("vk_tg1.db")
    with con :
        cur = con.cursor()
        cur.execute("SELECT name_dishes,count FROM Dishes WHERE count <=5")
        dishes_min_quantity = cur.fetchall()

        if dishes_min_quantity:
            message = "Продукты с маленьки количеством:\n"
            for products in dishes_min_quantity:
                name,count = products
                message+= f"{name}: {count}\n"

            return message
        else:
            return "Все продукты в достатке "




# def delete():
#     con = sl.connect("vk_tg1.db")
#     with con:
#         con.execute("""
#         DELETE FROM Dishes
#           """)
# delete()
#
# def create_table():
#     con = sl.connect("vk_tg1.db")
#     with con:
#         con.execute("""
#                     CREATE TABLE IF NOT EXISTS Dishes(
#                     id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
#                     name_dishes VARCHAR,
#                     count INTEGER,
#                     time VARCHAR,
#                     price VARCHAR);""")
#
#
def insert(name,count, time,price):
    con = sl.connect("vk_tg1.db")
    with con :
        con.execute("INSERT  INTO Dishes(name_dishes,count,time,price) VALUES(?,?,?,?)",[name,count,time,price])


def insert():
    con = sl.connect("vk_tg1.db")
    with con :
        con.execute("""DELETE FROM Users WHERE tg_id=718611792""")

# insert()


# insert("Борщ",20,15,7)
# insert("Суп с фрикадельками",20,15,5)
# insert("Гороховый суп",20,20,6)
# insert("Овсянка",20,20,5)
# insert("Гречка",20,10,5)
# insert("Рис",20,12,4)
# insert('Пицца "Маргарита"',20,25,18)
# insert('Пицца "Пепперони"',20,25,21)
# insert('Пицца "Италия"',20,30,23)
# insert("Cola",20,0,3)
# insert("Fanta",20,0,3)
# insert("Sprite",20,0,3)


#
#
#
#
def is_user_exest(user_id):
    con = sl.connect("vk_tg1.db")
    with con :
        result = con.execute("SELECT 1 FROM Users WHERE tg_id = ?", (str(user_id),)).fetchone()
        return result is not None

# def insert_user_data( user_id, user_name):
#     con = sl.connect("vk_tg1.db")
#     with con:
#         con.execute("""
#             INSERT INTO ADMIN (tg_id, status)
#             VALUES (?, ?);
#         """, (str(user_id), user_name))


