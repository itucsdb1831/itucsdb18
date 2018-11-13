import psycopg2 as dbapi2
from user import User
from game import Game
from game_of_user import GameOfUser
from item import Item
from review import Review
from friend import Friend
from friend_request import FriendRequest


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
  
  
def get_user_id(user_name):
    user_id = None
    connection = dbapi2.connect(dsn)
    cursor = connection.cursor()
    statement = "SELECT USER_ID FROM USERS WHERE NAME = %s"
    cursor.execute(statement, [user_name])
    if cursor.rowcount != 0:
        row = cursor.fetchone()
        user_id = row[0]
    cursor.close()
    connection.close()
    return user_id

  
def insert_review(review):
    connection = dbapi2.connect(dsn)
    cursor = connection.cursor()
    statement = """INSERT INTO REVIEWS (USER_ID, GAME_ID, LABEL, CONTENT) VALUES (%s, %s, %s, %s)"""
    data = ( review.user_id, review.game_id, review.label, review.content)
    cursor.execute(statement, data)
    connection.commit()
    cursor.close()
    connection.close()


def get_reviews4game(game_id):
    connection = dbapi2.connect(dsn)
    cursor = connection.cursor()
    statement = """SELECT REVIEW_ID, USER_ID, LABEL, CONTENT, LIKES, DISLIKES FROM REVIEWS WHERE GAME_ID=%s"""
    data = (game_id, )
    cursor.execute(statement, data)
    reviews = []
    for row in cursor:
        review_id, user_id, label, content, likes, dislikes = row
        reviews.append(Review(user_id, game_id, label, content, likes, dislikes, review_id))
    cursor.close()
    connection.close()
    return reviews

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
        game = GameOfUser(user_id_, game_id, title, time_played, time_purchased, num_of_reviews,  num_of_screenshots,
                          is_favourite)
        games.append(game)
    cursor.close()
    connection.close()
    return games

  
def check_code(code):
    valid = False
    connection = dbapi2.connect(dsn)
    cursor = connection.cursor()
    statement = "SELECT * FROM BALANCE_CODES WHERE CODE = %s"
    cursor.execute(statement, [code])
    if cursor.rowcount != 0:
        valid = True
    cursor.close()
    connection.close()
    return valid


def add_balance_to_user(user_id):
    connection = dbapi2.connect(dsn)
    cursor = connection.cursor()
    statement = "UPDATE USERS" \
                + " SET BALANCE = BALANCE + 100" \
                + " WHERE (USER_ID = %s)"
    cursor.execute(statement, [user_id])
    connection.commit()
    cursor.close()
    connection.close()


def decrease_balance_of_user(user_id, amount):
    connection = dbapi2.connect(dsn)
    cursor = connection.cursor()
    statement = "UPDATE USERS" \
                + " SET BALANCE = BALANCE - %s" \
                + " WHERE (USER_ID = %s)"
    data = (amount, user_id)
    cursor.execute(statement, data)
    connection.commit()
    cursor.close()
    connection.close()


def add_item(item):
    connection = dbapi2.connect(dsn)
    cursor = connection.cursor()
    statement = """INSERT INTO ITEMS (GAME_ID, NAME, RARITY, LEVEL) VALUES (%s, %s, %s, %s)"""
    data = (item.game_id, item.name, item.rarity, item.level)
    cursor.execute(statement, data)
    connection.commit()
    cursor.close()
    connection.close()


def get_items(game_id):
    items = []
    connection = dbapi2.connect(dsn)
    cursor = connection.cursor()
    statement = "SELECT * FROM ITEMS WHERE GAME_ID=%s"
    cursor.execute(statement, [game_id])

    for row in cursor:
        (item_id, _, name, rarity, level) = row
        item = Item(item_id, game_id, name, rarity, level)
        items.append(item)

    cursor.close()
    connection.close()
    return items


def delete_item(item_id):
    connection = dbapi2.connect(dsn)
    cursor = connection.cursor()
    statement = """DELETE FROM ITEMS WHERE ITEM_ID=%s"""
    cursor.execute(statement, [item_id])
    connection.commit()
    cursor.close()
    connection.close()


# -------------------------------------------------------


def send_friend_request(user_id_from, user_id_to):
    connection = dbapi2.connect(dsn)
    cursor = connection.cursor()
    statement = "INSERT INTO FRIEND_REQUESTS VALUES(%s, %s)"
    data = (user_id_from, user_id_to)
    cursor.execute(statement, data)
    connection.commit()
    cursor.close()
    connection.close()


def add_friend(user1_id, user2_id):
    connection = dbapi2.connect(dsn)
    cursor = connection.cursor()
    statement = "INSERT INTO FRIENDS(USER1_ID, USER2_ID, DATE_BEFRIENDED) VALUES(%s, %s, CURRENT_DATE)"
    data = (user1_id, user2_id)
    cursor.execute(statement, data)
    data = (user2_id, user1_id)
    cursor.execute(statement, data)
    connection.commit()
    cursor.close()
    connection.close()


def get_friend_requests(user_id_to):
    requests = []
    connection = dbapi2.connect(dsn)
    cursor = connection.cursor()
    statement = "SELECT USER_ID_FROM FROM FRIEND_REQUESTS WHERE USER_ID_TO = %s"
    cursor.execute(statement, [user_id_to])
    for row in cursor:
        user_id_from = row[0]
        request = FriendRequest(user_id_from, user_id_to)
        requests.append(request)
    cursor.close()
    connection.close()
    return requests


def remove_request(user_id_from, user_id_to):
    connection = dbapi2.connect(dsn)
    cursor = connection.cursor()
    statement = "DELETE FROM FRIEND_REQUESTS WHERE (USER_ID_FROM = %s) AND (USER_ID_TO = %s)"
    data = (user_id_from, user_id_to)
    cursor.execute(statement, data)
    connection.commit()
    cursor.close()
    connection.close()


def get_friends(user_id):
    friends = []
    connection = dbapi2.connect(dsn)
    cursor = connection.cursor()
    statement = "SELECT * FROM FRIENDS WHERE USER1_ID = %s"
    cursor.execute(statement, [user_id])
    for row in cursor:
        user1_id = row[0]
        user2_id = row[1]
        date_befriended = row[2]
        is_blocked = row[3]
        is_following = row[4]
        num_of_shared_games = row[5]
        is_favourite = row[6]
        friend = Friend(user1_id, user2_id, date_befriended, is_blocked, is_following,
                        num_of_shared_games, is_favourite)
        friends.append(friend)
    cursor.close()
    connection.close()
    return friends


def check_if_already_friends(user1_id, user2_id):
    are_friends = False
    connection = dbapi2.connect(dsn)
    cursor = connection.cursor()
    statement = "SELECT * FROM FRIENDS WHERE (USER1_ID = %s) AND (USER2_ID = %s)"
    data = (user1_id, user2_id)
    cursor.execute(statement, data)
    if cursor.rowcount != 0:
        are_friends = True
    cursor.close()
    connection.close()
    return are_friends


def check_friend_request(user_id_from, user_id_to):
    already_sent = False
    connection = dbapi2.connect(dsn)
    cursor = connection.cursor()
    statement = "SELECT * FROM FRIEND_REQUESTS WHERE (USER_ID_FROM = %s) AND (USER_ID_TO = %s)"
    data = (user_id_from, user_id_to)
    cursor.execute(statement, data)
    if cursor.rowcount != 0:
        already_sent = True
    cursor.close()
    connection.close()
    return already_sent

# def update_shared_games():


# def cancel_friend_request():






