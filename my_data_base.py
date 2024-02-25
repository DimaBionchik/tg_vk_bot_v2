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
    final_price = 0
    final_price+=total_price
    return f"{name}: количество {quantity} ., цена за штуку {price_per_unit}  ., время приготовления {time} ,конечная цена  {total_price}  "

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


def create_new_table(answer):
    con = sl.connect("vk_tg1.db")
    with con:
        con.execute("""
                    CREATE TABLE IF NOT EXISTS Dishes_answer(
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    id_dishes VARCHAR,
                    answer VARCHAR,
                    Rate VARCHAR );
                    """)


def create_new_tables():
    con = sl.connect("vk_tg1.db")
    with con:
        con.execute("""
                    CREATE TABLE IF NOT EXISTS Dishes_answer(
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    basket VARCHAR,
                    id_person VARCHAR,
                    feedback VARCHAR,
                    rate VARCHAR );
                    """)


def insert(name,count, time,price):
    con = sl.connect("vk_tg1.db")
    with con :
        con.execute("INSERT  INTO Dishes(name_dishes,count,time,price) VALUES(?,?,?,?)",[name,count,time,price])

def add_new_admin(id,status):
    con = sl.connect("vk_tg1.db")
    with con:
        con.execute("INSERT  INTO ADMIN(tg_id,status) VALUES(?,?)", [id,status])
def insert():
    con = sl.connect("vk_tg1.db")
    with con :
        con.execute("""DELETE FROM Users WHERE tg_id=718611792""")



def inserts():
    con = sl.connect("vk_tg1.db")
    with con :
        con.execute("""DELETE FROM ADMIN WHERE tg_id=718611792""")



def delete(admin_id):
    con = sl.connect("vk_tg1.db")
    with con :
        con.execute(f"DELETE FROM ADMIN WHERE tg_id={admin_id}")



# insert()
# inserts()

def insert_into_disches(name,count,time,price):
    con = sl.connect("vk_tg1.db")
    with con:
        con.execute("INSERT  INTO Dishes(name_dishes,count,time,price) VALUES(?,?,?,?)", [name,count,time,price])

def insert_into_disches_answer(basket,id,fedback):
    con = sl.connect("vk_tg1.db")
    with con:
        con.execute("INSERT  INTO Dishes_answer(basket,id_person,feedback) VALUES(?,?,?)",[basket, id,fedback])










def is_user_exest(user_id):
    con = sl.connect("vk_tg1.db")
    with con :
        result = con.execute("SELECT 1 FROM Users WHERE tg_id = ?", (str(user_id),)).fetchone()
        return result is not None

def is_admin_exest(admin_id):
    con = sl.connect("vk_tg1.db")
    with con:
        result = con.execute("SELECT 1 FROM ADMIN WHERE tg_id = ?", (str(admin_id),)).fetchone()
        return result is not None


def is_super_admin(ad_id):
    con = sl.connect("vk_tg1.db")
    with con:
        result = con.execute("SELECT 1 FROM ADMIN WHERE tg_id = ?", (str(ad_id),)).fetchone()
        return result is not None


def get_order(user_id):
    con = sl.connect("vk_tg1.db")
    with con:
        result = con.execute("SELECT BASKET FROM Users WHERE tg_id =?", (str(user_id),)).fetchone()
        return result







