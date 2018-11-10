import psycopg2 as dbapi2
from user import User
from game import Game
from game_of_user import GameOfUser

dsn = """user=khxcpxyuayifiy password=a71d836a4a3e8c9d4030a8bd40ffec8d7e43202bf75ece49c4635701c10cd21f
host=ec2-54-247-124-154.eu-west-1.compute.amazonaws.com port=5432 dbname=dd7j2nqkjb2bs9"""


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
    user_id, name, password, is_active, is_admin, balance = cursor.fetchone()
    user = User(name, password, is_active, is_admin, balance, user_id)
    cursor.close()
    connection.close()
    return user


def get_user(user_id):
    connection = dbapi2.connect(dsn)
    cursor = connection.cursor()
    statement = """SELECT * FROM USERS WHERE USER_ID=%s"""
    data = (user_id, )
    cursor.execute(statement, data)
    if cursor.rowcount != 0:
        user_id, name, password, is_active, is_admin, balance = cursor.fetchone()
        userch = User(name, password, is_active, is_admin, balance, user_id)
    else:
        userch = None
    cursor.close()
    connection.close()
    return userch

# -------------------------------------------------------


def add_game(game):
    connection = dbapi2.connect(dsn)
    cursor = connection.cursor()
    statement = "INSERT INTO GAMES (TITLE, GENRE, AGE_RESTRICTION, PRICE) VALUES (%s, %s, %s, %s)"
    data = (game.title, game.genre, game.age_restriction, game.price)
    cursor.execute(statement, data)
    connection.commit()
    cursor.close()
    connection.close()


def get_game(game_id):
    connection = dbapi2.connect(dsn)
    cursor = connection.cursor()
    statement = "SELECT * FROM GAMES WHERE GAME_ID=%s"
    cursor.execute(statement, [game_id])
    if cursor is not None:
        game_id, title, genre, rating, votes, age_restriction, price = cursor.fetchone()
        game = Game(game_id, title, genre, rating, votes, age_restriction, price)
    else:
        game = None
    cursor.close()
    connection.close()
    return game


def get_games():
    games = []
    connection = dbapi2.connect(dsn)
    cursor = connection.cursor()
    statement = "SELECT * FROM GAMES"
    cursor.execute(statement)
    for row in cursor:
        game_id = row[0]
        title = row[1]
        genre = row[2]
        rating = row[3]
        votes = row[4]
        age_restriction = row[5]
        price = row[6]
        game_ = Game(game_id, title, genre, rating, votes, age_restriction, price)
        games.append(game_)
    return games


def update_rating_of_game(game_id, rating):
    connection = dbapi2.connect(dsn)
    cursor = connection.cursor()
    statement = "UPDATE GAMES" \
                + " SET RATING = (RATING * VOTES + %s) / (VOTES + 1)," \
                + " VOTES = VOTES + 1" \
                + " WHERE (GAME_ID = %s)"
    data = (rating, game_id)
    cursor.execute(statement, data)
    connection.commit()
    cursor.close()
    connection.close()


def delete_game(game_id):
    connection = dbapi2.connect(dsn)
    cursor = connection.cursor()
    statement = "DELETE FROM GAMES WHERE GAME_ID = %s"
    cursor.execute(statement, [game_id])
    statement = "DELETE FROM GAMES_OF_USERS WHERE GAME_ID = %s"
    cursor.execute(statement, [game_id])
    connection.commit()
    cursor.close()
    connection.close()


def add_game_to_user(game_id, user_id):
    success = False
    connection = dbapi2.connect(dsn)
    cursor = connection.cursor()
    statement = "SELECT * FROM GAMES_OF_USERS WHERE (GAME_ID = %s) AND (USER_ID = %s)"
    data = (game_id, user_id)
    cursor.execute(statement, data)
    if cursor.rowcount == 0:
        game = get_game(game_id)
        statement = "INSERT INTO GAMES_OF_USERS(USER_ID, GAME_ID, TITLE, TIME_PURCHASED) VALUES(%s, %s, %s, CURRENT_DATE)"
        data = (user_id, game_id, game.title)
        cursor.execute(statement, data)
        success = True
    connection.commit()
    cursor.close()
    connection.close()
    return success


def get_games_of_user(user_id):
    games = []
    connection = dbapi2.connect(dsn)
    cursor = connection.cursor()
    statement = "SELECT * FROM GAMES_OF_USERS WHERE USER_ID = %s"
    cursor.execute(statement, [user_id])
    for row in cursor:
        user_id_ = row[0]
        game_id = row[1]
        title = row[2]
        time_played = row[3]
        time_purchased = row[4]
        num_of_reviews = row[5]
        num_of_screenshots = row[6]
        is_favourite = row[7]
        game = GameOfUser(user_id_, game_id, title, time_played, time_purchased, num_of_reviews,  num_of_screenshots, is_favourite)
        games.append(game)
    cursor.close()
    connection.close()
    return games

