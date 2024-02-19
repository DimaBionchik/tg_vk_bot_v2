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

upd("Суп с фрикадельками", 2)
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
# def insert(con,id,name ,tel,adress):
#     with con :
#         con.execute("INSERT OR IGNORE INTO Users(tg_id,name,tel,adress) VALUES(?,?,?,?)",[id,name,tel,adress])
#
#
#
#
# def is_user_exest(user_id):
#     con = sl.connect("vk_tg1.db")
#     with con :
#         result = con.execute("SELECT 1 FROM Users WHERE tg_id = ?", (str(user_id),)).fetchone()
#         return result is not None
#
# def insert_user_data( user_id, user_name):
#     con = sl.connect("vk_tg1.db")
#     with con:
#         con.execute("""
#             INSERT INTO ADMIN (tg_id, status)
#             VALUES (?, ?);
#         """, (str(user_id), user_name))


