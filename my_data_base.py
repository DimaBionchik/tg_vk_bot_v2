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

def insert(con,id,name ,tel,adress):
    with con :
        con.execute("INSERT OR IGNORE INTO Users(tg_id,name,tel,adress) VALUES(?,?,?,?)",[id,name,tel,adress])



# def select_all_from_table(name_tabel:str):
#     with con :
#
def is_user_exest(user_id):
    con = sl.connect("vk_tg1.db")
    with con :
        result = con.execute("SELECT 1 FROM Users WHERE tg_id = ?", (str(user_id),)).fetchone()
        return result is not None

def insert_user_data( user_id, user_name):
    con = sl.connect("vk_tg1.db")
    with con:
        con.execute("""
            INSERT INTO ADMIN (tg_id, status) 
            VALUES (?, ?);
        """, (str(user_id), user_name))


# insert_user_data(718611792,"суперАдмин ")
# create_con(con)