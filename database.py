import psycopg2 as dbapi2
from user import User

dsn = """user=erfybxxvnizudu password=35d55b4417e736e6493eb90e4f674f8530afd4d6c071c675811fd7ee5240557c
host=ec2-204-236-230-19.compute-1.amazonaws.com port=5432 dbname=d7qite4opgg4jv"""

def communicate_with_db(statement):
    connection = dbapi2.connect(dsn)
    cursor = connection.cursor()
    cursor.execute(statement)
    connection.commit()
    cursor.close()
    connection.close()
    return cursor

def insert_user(user4insert):
    connection = dbapi2.connect(dsn)
    cursor = connection.cursor()
    statement = """INSERT INTO USERS (NAME, PASSWORD) VALUES (%s, %s)"""
    data = (user4insert.get_user_name(), user4insert.get_pw(),)
    cursor.execute(statement, data)
    connection.commit()
    cursor.close()
    connection.close()


def query_user_name(user_name):
    connection = dbapi2.connect(dsn)
    cursor = connection.cursor()
    statement ="""SELECT * FROM USERS WHERE NAME=%s"""
    user_name = (user_name, )
    cursor.execute(statement, user_name)
    if cursor.rowcount == 0:
        cursor.close()
        connection.close()
        return None
    print(cursor)
    user_id, name, password = cursor.fetchone()
    user = User(name, password, user_id)
    cursor.close()
    connection.close()
    return user

def get_user(user_id):
    connection = dbapi2.connect(dsn)
    cursor = connection.cursor()
    statement = """SELECT * FROM USERS WHERE USER_ID=%s"""
    data = (user_id, )
    cursor.execute(statement, data)
    if cursor != None:
        user_id, name, password = cursor.fetchone()
        userch = User(name, password, user_id)
    else:
        userch = None
    cursor.close()
    connection.close()
    return userch
    

