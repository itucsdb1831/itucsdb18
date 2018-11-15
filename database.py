import psycopg2 as dbapi2
from user import User
from game import Game
from game_of_user import GameOfUser
from item import Item
from review import Review
from friend import Friend
from friend_request import FriendRequest


class Database:
    def __init__(self, dsn):
        self.dsn = dsn
        self.connection = None
        self.cursor = None

    def connect(self):
        self.connection = dbapi2.connect(self.dsn)
        self.cursor = self.connection.cursor()

    def query_database(self, query):
        statement, data = query
        self.cursor.execute(statement, data)
        self.connection.commit()

    def disconnect(self):
        self.cursor.close()
        self.connection.close()

    def insert_user(self, user_to_insert):
        self.connect()

        statement = """INSERT INTO USERS (NAME, PASSWORD) VALUES (%s, %s)"""
        data = (user_to_insert.get_user_name(), user_to_insert.get_pw(),)
        query = statement, data
        self.query_database(query)

        self.disconnect()

    def query_user_name(self, user_name):
        self.connect()

        statement = """SELECT * FROM USERS WHERE NAME=%s"""
        data = (user_name,)
        query = statement, data
        self.query_database(query)

        user_id, name, password, is_active, is_admin, balance = self.cursor.fetchone()
        user = User(name, password, is_active, is_admin, balance, user_id)

        self.disconnect()
        return user

    def get_user(self, user_id):
        self.connect()

        statement = """SELECT * FROM USERS WHERE USER_ID=%s"""
        data = (user_id,)
        query = statement, data
        self.query_database(query)

        user_id, name, password, is_active, is_admin, balance = self.cursor.fetchone()
        user = User(name, password, is_active, is_admin, balance, user_id)

        self.disconnect()
        return user

    def get_user_id(self, user_name):
        self.connect()

        statement = "SELECT USER_ID FROM USERS WHERE NAME = %s"
        data = [user_name]
        query = statement, data
        self.query_database(query)

        row = self.cursor.fetchone()
        user_id = row[0]

        self.disconnect()
        return user_id

    def insert_review(self, review):
        self.connect()

        statement = """INSERT INTO REVIEWS (USER_ID, GAME_ID, LABEL, CONTENT) VALUES (%s, %s, %s, %s)"""
        data = (review.user_id, review.game_id, review.label, review.content)
        query = statement, data
        self.query_database(query)

        self.disconnect()

    def get_reviews_of_game(self, game_id):
        self.connect()

        statement = """SELECT REVIEW_ID, USER_ID, LABEL, CONTENT, LIKES, DISLIKES FROM REVIEWS WHERE GAME_ID=%s"""
        data = (game_id,)
        query = statement, data
        self.query_database(query)

        reviews = []
        for row in self.cursor:
            review_id, user_id, label, content, likes, dislikes = row
            reviews.append(Review(user_id, game_id, label, content, likes, dislikes, review_id))

        self.disconnect()
        return reviews

    # -------------------------------------------------------

    def add_game(self, game):
        self.connect()

        statement = "INSERT INTO GAMES (TITLE, GENRE, AGE_RESTRICTION, PRICE) VALUES (%s, %s, %s, %s)"
        data = (game.title, game.genre, game.age_restriction, game.price)
        query = statement, data
        self.query_database(query)

        self.disconnect()

    def get_game(self, game_id):
        self.connect()

        statement = "SELECT * FROM GAMES WHERE GAME_ID=%s"
        data = [game_id]
        query = statement, data
        self.query_database(query)

        if self.cursor is not None:
            game_id, title, genre, rating, votes, age_restriction, price = self.cursor.fetchone()
            game = Game(game_id, title, genre, rating, votes, age_restriction, price)
        else:
            game = None

        self.disconnect()
        return game

    def get_games(self):
        self.connect()

        statement = "SELECT * FROM GAMES"
        self.cursor.execute(statement)

        games = []
        for row in self.cursor:
            (game_id, title, genre, rating, votes, age_restriction, price) = row
            game_ = Game(game_id, title, genre, rating, votes, age_restriction, price)
            games.append(game_)
        return games

    def update_rating_of_game(self, game_id, rating):
        self.connect()

        statement = "UPDATE GAMES" \
                    + " SET RATING = (RATING * VOTES + %s) / (VOTES + 1)," \
                    + " VOTES = VOTES + 1" \
                    + " WHERE (GAME_ID = %s)"
        data = (rating, game_id)
        query = statement, data
        self.query_database(query)

        self.disconnect()

    def delete_game(self, game_id):
        self.connect()

        statement = "DELETE FROM GAMES WHERE GAME_ID = %s"
        data = [game_id]
        query = statement, data
        self.query_database(query)

        statement = "DELETE FROM GAMES_OF_USERS WHERE GAME_ID = %s"
        query = statement, data
        self.query_database(query)

        self.disconnect()

    def add_game_to_user(self, game_id, user_id):
        self.connect()

        statement = "SELECT * FROM GAMES_OF_USERS WHERE (GAME_ID = %s) AND (USER_ID = %s)"
        data = (game_id, user_id)
        query = statement, data
        self.query_database(query)

        is_successful = self.cursor.rowcount == 0
        if is_successful:
            game = self.get_game(game_id)
            statement = "INSERT INTO GAMES_OF_USERS(USER_ID, GAME_ID, TITLE, TIME_PURCHASED) VALUES(%s, %s, %s, CURRENT_DATE)"
            data = (user_id, game_id, game.title)
            query = statement, data
            self.query_database(query)

        self.disconnect()
        return is_successful

    def get_games_of_user(self, user_id):
        self.connect()

        statement = "SELECT * FROM GAMES_OF_USERS WHERE USER_ID = %s"
        data = [user_id]
        query = statement, data
        self.query_database(query)

        games = []
        for row in self.cursor:
            (user_id_, game_id, title, time_played, time_purchased, num_of_reviews, num_of_screenshots, is_favourite) = row
            game = GameOfUser(user_id_, game_id, title, time_played, time_purchased, num_of_reviews, num_of_screenshots,
                              is_favourite)
            games.append(game)

        self.disconnect()
        return games

    def check_code(self, code):
        self.connect()

        statement = "SELECT * FROM BALANCE_CODES WHERE CODE = %s"
        data = [code]
        query = statement, data
        self.query_database(query)

        is_valid = self.cursor.rowcount != 0

        self.disconnect()
        return is_valid

    def add_balance_to_user(self, user_id):
        self.connect()

        statement = "UPDATE USERS" \
                    + " SET BALANCE = BALANCE + 100" \
                    + " WHERE (USER_ID = %s)"
        data = [user_id]
        query = statement, data
        self.query_database(query)

        self.disconnect()

    def decrease_balance_of_user(self, user_id, amount):
        self.connect()

        statement = "UPDATE USERS" \
                    + " SET BALANCE = BALANCE - %s" \
                    + " WHERE (USER_ID = %s)"
        data = (amount, user_id)
        query = statement, data
        self.query_database(query)

        self.disconnect()

    def add_item(self, item):
        self.connect()

        statement = """INSERT INTO ITEMS (GAME_ID, NAME, RARITY, LEVEL) VALUES (%s, %s, %s, %s)"""
        data = (item.game_id, item.name, item.rarity, item.level)
        query = statement, data
        self.query_database(query)

        self.disconnect()

    def get_items(self, game_id):
        self.connect()

        statement = "SELECT * FROM ITEMS WHERE GAME_ID=%s"
        data = [game_id]
        query = statement, data
        self.query_database(query)

        items = []
        for row in self.cursor:
            (item_id, _, name, rarity, level) = row
            item = Item(item_id, game_id, name, rarity, level)
            items.append(item)

        self.disconnect()
        return items

    def delete_item(self, item_id):
        self.connect()

        statement = """DELETE FROM ITEMS WHERE ITEM_ID=%s"""
        data = [item_id]
        query = statement, data
        self.query_database(query)

        self.disconnect()

    # -------------------------------------------------------

    def send_friend_request(self, user_id_from, user_id_to):
        self.connect()

        statement = "INSERT INTO FRIEND_REQUESTS VALUES(%s, %s)"
        data = (user_id_from, user_id_to)
        query = statement, data
        self.query_database(query)

        self.disconnect()

    def add_friend(self, user1_id, user2_id):
        self.connect()

        statement = "INSERT INTO FRIENDS(USER1_ID, USER2_ID, DATE_BEFRIENDED) VALUES(%s, %s, CURRENT_DATE)"
        data = (user1_id, user2_id)
        query = statement, data
        self.query_database(query)

        data = (user2_id, user1_id)
        query = statement, data
        self.query_database(query)

        self.disconnect()

    def get_friend_requests(self, user_id_to):
        self.connect()
        statement = "SELECT USER_ID_FROM FROM FRIEND_REQUESTS WHERE USER_ID_TO = %s"
        data = [user_id_to]
        query = statement, data
        self.query_database(query)

        requests = []
        for row in self.cursor:
            user_id_from = row[0]
            request = FriendRequest(user_id_from, user_id_to)
            requests.append(request)

        self.disconnect()
        return requests

    def remove_request(self, user_id_from, user_id_to):
        self.connect()

        statement = "DELETE FROM FRIEND_REQUESTS WHERE (USER_ID_FROM = %s) AND (USER_ID_TO = %s)"
        data = (user_id_from, user_id_to)
        query = statement, data
        self.query_database(query)

        self.disconnect()

    def get_friends(self, user_id):
        self.connect()

        statement = "SELECT * FROM FRIENDS WHERE USER1_ID = %s"
        data = [user_id]
        query = statement, data
        self.query_database(query)

        friends = []
        for row in self.cursor:
            (user1_id, user2_id, date_befriended, is_blocked, is_following,
             num_of_shared_games, is_favourite) = row
            friend = Friend(user1_id, user2_id, date_befriended, is_blocked, is_following,
                            num_of_shared_games, is_favourite)
            friends.append(friend)

        self.disconnect()
        return friends

    def check_if_already_friends(self, user1_id, user2_id):
        self.connect()

        statement = "SELECT * FROM FRIENDS WHERE (USER1_ID = %s) AND (USER2_ID = %s)"
        data = (user1_id, user2_id)
        query = statement, data
        self.query_database(query)

        are_friends = self.cursor.rowcount != 0

        self.disconnect()
        return are_friends

    def check_friend_request(self, user_id_from, user_id_to):
        self.connect()

        statement = "SELECT * FROM FRIEND_REQUESTS WHERE (USER_ID_FROM = %s) AND (USER_ID_TO = %s)"
        data = (user_id_from, user_id_to)
        query = statement, data
        self.query_database(query)

        already_sent = self.cursor.rowcount != 0

        self.disconnect()
        return already_sent

    # def update_shared_games():

    # def cancel_friend_request():
