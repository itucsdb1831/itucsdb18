import psycopg2 as dbapi2
from user import User
from game import Game
from game_of_user import GameOfUser
from item import Item
from review import Review
from friend import Friend
from friend_request import FriendRequest
from screenshot import Screenshot
from item_of_user import ItemOfUser


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
        try:
            self.cursor.execute(statement, data)
            self.connection.commit()
        except Exception as e:
            print(e)
            self.connect()
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
        if self.cursor.rowcount == 0:
            return None
        
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

        user = None
        if self.cursor.rowcount != 0:
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

        user_id = None
        if self.cursor.rowcount != 0:
            row = self.cursor.fetchone()
            user_id = row[0]

        self.disconnect()
        return user_id

    def insert_review(self, review):
        self.connect()

        statement = """INSERT INTO REVIEWS (USER_ID, GAME_ID, LABEL, CONTENT, ADDED) VALUES (%s, %s, %s, %s, %s)"""
        data = (review.user_id, review.game_id, review.label, review.content, review.added,)
        query = statement, data
        self.query_database(query)

        self.disconnect()

    def get_reviews_of_game(self, game_id, cur_user_id):
        self.connect()

        statement = """SELECT REVIEW_ID, USER_ID, LABEL, CONTENT, ADDED, LIKES, DISLIKES, UPDATED FROM REVIEWS WHERE GAME_ID=%s"""
        data = (game_id,)
        query = statement, data
        self.query_database(query)

        reviews = []
        for row in self.cursor:
            review_id, user_id, label, content, added, likes, dislikes, edited = row
            reviews.append(Review(user_id, game_id, label, added, content, likes, dislikes, edited, review_id))

        for review in reviews:
            review.liked_from_current = self.get_like_of_user(review.id, cur_user_id, "REVIEWS")
            review.disliked_from_current = self.get_dislike_of_user(review.id, cur_user_id, "REVIEWS")
        self.disconnect()
        return reviews
    
    def get_prev_review(self, game_id, user_id):
        self.connect()

        statement = """SELECT REVIEW_ID, USER_ID, LABEL, CONTENT, ADDED, LIKES, DISLIKES, UPDATED FROM REVIEWS WHERE GAME_ID=%s AND USER_ID=%s"""
        data = (game_id, str(user_id),)
        query = statement, data
        self.query_database(query)
        reviews = []
        for row in self.cursor:
            review_id, user_id, label, content, added, likes, dislikes, edited = row
            reviews.append(Review(user_id, game_id, label, added, content, likes, dislikes, edited, review_id))
        self.disconnect()
        return reviews
    
    def update_review(self, review_id, label, content, edited):
        self.connect()

        statement = """UPDATE REVIEWS SET CONTENT=%s, LABEL=%s, UPDATED=%s WHERE REVIEW_ID=%s"""
        data = (content, label, edited, review_id,)
        query = statement, data
        self.query_database(query)
        
        self.disconnect()
    
    def delete_review(self, review_id):
        self.connect()

        statement = """DELETE FROM REVIEWS WHERE REVIEW_ID=%s"""
        data = (review_id,)
        query = statement, data
        self.query_database(query)

        statement = """DELETE FROM LIKES WHERE ((ENTITY_ID=%s) AND (ENTITY_TYPE=%s))"""
        data = (review_id, "REVIEWS",)
        query = statement, data
        self.query_database(query)

        statement = """DELETE FROM DISLIKES WHERE ((ENTITY_ID=%s) AND (ENTITY_TYPE=%s))"""
        data = (review_id, "REVIEWS",)
        query = statement, data
        self.query_database(query)

        self. disconnect()
    
    def add_like(self, entity_id, user_id, entity_type):
        self.connect()
        statement = """INSERT INTO LIKES (ENTITY_ID, USER_ID, ENTITY_TYPE) VALUES (%s, %s, %s)"""
        data = (entity_id, user_id, entity_type,)
        query = statement, data
        self.query_database(query)
        
        statements = {"REVIEWS" : "UPDATE REVIEWS SET LIKES = LIKES + 1 WHERE REVIEW_ID=%s",
        "SCREENSHOTS" : "UPDATE SCREENSHOTS SET LIKES = LIKES + 1 WHERE SHOT_ID=%s"}
        data = (entity_id,)
        query = statements[entity_type], data
        self.query_database(query)
        self.disconnect()
    
    def remove_like(self, entity_id, user_id, entity_type):
        self.connect()
        statement = """DELETE FROM LIKES WHERE ((ENTITY_ID=%s) AND (USER_ID=%s) AND (ENTITY_TYPE=%s))"""
        data = (entity_id, user_id, entity_type,)
        query = statement, data
        self.query_database(query)

        statements = {"REVIEWS" : "UPDATE REVIEWS SET LIKES = LIKES - 1 WHERE REVIEW_ID=%s",
        "SCREENSHOTS" : "UPDATE SCREENSHOTS SET LIKES = LIKES - 1 WHERE SHOT_ID=%s"}
        data = (entity_id,)
        query = statements[entity_type], data
        self.query_database(query)
        self.disconnect()
    
    def get_like_of_user(self, entity_id, user_id, entity_type):
        self.connect()
        statement = """SELECT * FROM LIKES WHERE ((ENTITY_ID=%s) AND (USER_ID=%s) AND (ENTITY_TYPE=%s))"""
        data = (entity_id, user_id, entity_type,)
        query = statement, data
        self.query_database(query)
        
        is_liked = self.cursor.rowcount != 0
        self.disconnect()
        print(is_liked)
        return is_liked
    
    def add_dislike(self, entity_id, user_id, entity_type):
        self.connect()
        statement = """INSERT INTO DISLIKES (ENTITY_ID, USER_ID, ENTITY_TYPE) VALUES (%s, %s, %s)"""
        data = (entity_id, user_id, entity_type,)
        query = statement, data
        self.query_database(query)
        
        statements = {"REVIEWS" : "UPDATE REVIEWS SET DISLIKES = DISLIKES + 1 WHERE REVIEW_ID=%s",
        "SCREENSHOTS" : "UPDATE SCREENSHOTS SET DISLIKES = DISLIKES + 1 WHERE SHOT_ID=%s"}
        data = (entity_id,)
        query = statements[entity_type], data
        self.query_database(query)
        self.disconnect()
    
    def remove_dislike(self, entity_id, user_id, entity_type):
        self.connect()
        statement = """DELETE FROM DISLIKES WHERE ((ENTITY_ID=%s) AND (USER_ID=%s) AND (ENTITY_TYPE=%s))"""
        data = (entity_id, user_id, entity_type,)
        query = statement, data
        self.query_database(query)

        statements = {"REVIEWS" : "UPDATE REVIEWS SET DISLIKES = DISLIKES - 1 WHERE REVIEW_ID=%s",
        "SCREENSHOTS" : "UPDATE SCREENSHOTS SET DISLIKES = DISLIKES - 1 WHERE SHOT_ID=%s"}
        data = (entity_id,)
        query = statements[entity_type], data
        self.query_database(query)
        self.disconnect()
    
    def get_dislike_of_user(self, entity_id, user_id, entity_type):
        self.connect()
        statement = """SELECT * FROM DISLIKES WHERE ((ENTITY_ID=%s) AND (USER_ID=%s) AND (ENTITY_TYPE=%s))"""
        data = (entity_id, user_id, entity_type,)
        query = statement, data
        self.query_database(query)
        is_disliked = self.cursor.rowcount != 0

        self.disconnect()
        print(is_disliked)
        return is_disliked
    
    def insert_screenshot(self, ss):
        self.connect()

        statement = "INSERT INTO SCREENSHOTS (NAME, USER_ID, GAME_ID, CAPTION, DATE_ADDED, LIKES, DISLIKES) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        data = (ss.name, ss.user_id, ss.game_id, ss.caption, ss.date_added, ss.likes, ss.dislikes,)
        query = statement, data
        self.query_database(query)
        self.disconnect()
    
    def get_screenshots_of_game(self, game_id, cur_user_id):
        self.connect()

        statement = "SELECT NAME, USER_ID, CAPTION, DATE_ADDED, LIKES, DISLIKES, SHOT_ID FROM SCREENSHOTS WHERE GAME_ID=%s"
        data = (str(game_id),)
        query = statement, data
        self.query_database(query)
        sss = []
        for row in self.cursor:
            name, user_id, caption, date_added, likes, dislikes, shot_id = row
            sss.append(Screenshot(name, user_id, game_id, caption, date_added, likes, dislikes, shot_id))
        
        for shot in sss:
            shot.liked_from_current = self.get_like_of_user(shot.id, cur_user_id, "SCREENSHOTS")
            shot.disliked_from_current = self.get_dislike_of_user(shot.id, cur_user_id, "SCREENSHOTS")
        self.disconnect()
        return sss
    
    def delete_screenshot(self, shot_name):
        self.connect()

        statement = "DELETE FROM SCREENSHOTS WHERE NAME=%s"
        data = (shot_name,)
        query = statement, data
        self.query_database(query)

        self.disconnect()

    # -------------------------------------------------------

    def add_game(self, game):
        self.connect()

        statement = "INSERT INTO GAMES (TITLE, GENRE, AGE_RESTRICTION, PRICE) VALUES (%s, %s, %s, %s)"
        data = (game.title, game.genre, game.age_restriction, game.price,)
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

    def update_rating_of_game(self, game_id, user_id, rating, already_rated):
        self.connect()

        new_rating = rating
        if already_rated:
            previous_rating = self.get_user_rating(game_id, user_id)
            new_rating = rating - previous_rating

        statement = "UPDATE GAMES" \
                    + " SET RATING = (RATING * VOTES + %s) / (VOTES + 1)," \
                    + " VOTES = VOTES + 1" \
                    + " WHERE (GAME_ID = %s)"

        data = (new_rating, game_id,)
        query = statement, data
        self.query_database(query)

        self.disconnect()

    def get_user_rating(self, game_id, user_id):
        self.connect()

        statement = "SELECT * FROM RATING_VOTES WHERE (USER_ID = %s) AND (GAME_ID = %s)"
        data = (game_id, user_id,)
        query = statement, data
        self.query_database(query)

        user_rating = None
        if self.cursor is not None:
            user_rating = self.cursor.fetchone()[2]

        self.disconnect()
        return user_rating

    def is_already_rated(self, user_id, game_id):
        self.connect()

        statement = "SELECT * FROM RATING_VOTES WHERE (USER_ID = %s) AND (GAME_ID = %s)"
        data = (game_id, user_id,)
        query = statement, data
        self.query_database(query)

        already_rated = self.cursor is None

        self.disconnect()
        return already_rated

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
        data = (game_id, user_id,)
        query = statement, data
        self.query_database(query)

        is_successful = self.cursor.rowcount == 0
        if is_successful:
            game = self.get_game(game_id)
            statement = "INSERT INTO GAMES_OF_USERS(USER_ID, GAME_ID, TITLE, TIME_PURCHASED) VALUES(%s, %s, %s, CURRENT_DATE)"
            data = (user_id, game_id, game.title,)
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
        data = (amount, user_id,)
        query = statement, data
        self.query_database(query)

        self.disconnect()

    def add_item(self, item):
        self.connect()

        statement = """INSERT INTO ITEMS (GAME_ID, PICTURE, NAME, ITEM_TYPE, RARITY, PRICE)
                           VALUES (%s, %s, %s, %s, %s, %s)"""
        data = (item.game_id, item.picture, item.name, item.item_type, item.rarity, item.price)

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
            (item_id, _, picture, name, item_type, rarity, price) = row
            item = Item(item_id, game_id, picture, name, item_type, rarity, price)
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

    def get_item(self, game_id, item_id):
        self.connect()
        statement = "SELECT * FROM ITEMS WHERE (GAME_ID=%s) AND (ITEM_ID=%s)"
        data = [game_id, item_id]
        query = statement, data
        self.query_database(query)

        if self.cursor is not None:
            (item_id, game_id, picture, name, item_type, rarity, price) = self.cursor.fetchone()
            item = Item(item_id, game_id, picture, name, item_type, rarity, price)
        else:
            item = None

        self.disconnect()
        return item

    def add_item_to_user(self, item_id, game_id, user_id):
        self.connect()

        statement = """SELECT * FROM ITEMS_OF_USERS WHERE (ITEM_ID = %s) AND USER_ID = %s"""
        data = (item_id, user_id)
        query = statement, data
        self.query_database(query)

        already_has_item = self.cursor.rowcount != 0
        if already_has_item:
            statement = """UPDATE ITEMS_OF_USERS
                               SET LEVEL = LEVEL + 1
                               WHERE ITEM_ID = %s AND USER_ID = %s;"""
            query = statement, data
            self.query_database(query)
        else:
            item = self.get_item(game_id, item_id)
            statement = """INSERT INTO ITEMS_OF_USERS(ITEM_ID, GAME_ID, USER_ID, NAME, DATE_PURCHASED)
                               VALUES(%s, %s, %s, %s, CURRENT_DATE)"""
            data = (item_id, game_id, user_id, item.name)
            query = statement, data
            self.query_database(query)

        self.disconnect()
        return already_has_item

    def get_items_of_user(self, user_id):
        self.connect()

        statement = """SELECT * FROM ITEMS_OF_USERS WHERE USER_ID = %s"""
        data = [user_id]
        query = statement, data
        self.query_database(query)

        items_of_user = []
        for row in self.cursor:
            (item_id, game_id, user_id, name, level, color, is_equipped, is_favorite, date_purchased) = row
            item = ItemOfUser(item_id, game_id, user_id, name, level, color, is_equipped, is_favorite, date_purchased)
            items_of_user.append(item)

        self.disconnect()
        return items_of_user

    def edit_item(self, item_id, new_color, new_status, is_equipped):
        self.connect()

        if new_status == "TRUE":
            statement = """UPDATE ITEMS_OF_USERS
                               SET IS_FAVORITE = FALSE
                               WHERE IS_FAVORITE = TRUE"""
            query = statement, []
            self.query_database(query)

        statement = """UPDATE ITEMS_OF_USERS
                           SET COLOR = %s, IS_FAVORITE = %s, IS_EQUIPPED = %s
                           WHERE ITEM_ID = %s;
                    """
        data = [new_color, new_status, is_equipped, item_id]
        query = statement, data
        self.query_database(query)

        self.disconnect()

    # -------------------------------------------------------

    def send_friend_request(self, user_id_from, user_id_to):
        user_name_from = self.get_user(user_id_from).user_name
        user_name_to = self.get_user(user_id_to).user_name
        self.connect()

        statement = "INSERT INTO FRIEND_REQUESTS VALUES(%s, %s, %s, %s)"
        data = (user_id_from, user_id_to, user_name_from, user_name_to)
        query = statement, data
        self.query_database(query)

        self.disconnect()

    def add_friend(self, user1_id, user2_id):
        user2_name = self.get_user(user2_id).user_name
        user1_name = self.get_user(user1_id).user_name
        self.connect()

        statement = "INSERT INTO FRIENDS(USER1_ID, USER2_ID, USER2_NAME, DATE_BEFRIENDED)" \
                    " VALUES(%s, %s, %s, CURRENT_DATE)"
        data = (user1_id, user2_id, user2_name,)
        query = statement, data
        self.query_database(query)

        data = (user2_id, user1_id, user1_name)
        query = statement, data
        self.query_database(query)

        self.disconnect()

    def get_received_friend_requests(self, user_id_to):
        self.connect()
        statement = "SELECT * FROM FRIEND_REQUESTS WHERE USER_ID_TO = %s"
        data = [user_id_to]
        query = statement, data
        self.query_database(query)

        requests = []
        for row in self.cursor:
            user_id_from = row[0]
            user_name_from = row[2]
            user_name_to = row[3]
            request = FriendRequest(user_id_from, user_name_from, user_id_to, user_name_to)
            requests.append(request)

        self.disconnect()
        return requests

    def get_sent_friend_requests(self, user_id_from):
        self.connect()
        statement = "SELECT * FROM FRIEND_REQUESTS WHERE USER_ID_FROM = %s"
        data = [user_id_from]
        query = statement, data
        self.query_database(query)

        requests = []
        for row in self.cursor:
            user_id_to = row[1]
            user_name_from = row[2]
            user_name_to = row[3]
            request = FriendRequest(user_id_from, user_name_from, user_id_to, user_name_to)
            requests.append(request)

        self.disconnect()
        return requests

    def remove_request(self, user_id_from, user_id_to):
        self.connect()

        statement = "DELETE FROM FRIEND_REQUESTS WHERE (USER_ID_FROM = %s) AND (USER_ID_TO = %s)"
        data = (user_id_from, user_id_to,)
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
            (user1_id, user2_id, user2_name, date_befriended, is_blocked, is_following,
             num_of_shared_games, is_favourite) = row
            friend = Friend(user1_id, user2_id, user2_name, date_befriended, is_blocked, is_following,
                            num_of_shared_games, is_favourite)
            friends.append(friend)

        self.disconnect()
        return friends

    def check_if_already_friends(self, user1_id, user2_id):
        self.connect()

        statement = "SELECT * FROM FRIENDS WHERE (USER1_ID = %s) AND (USER2_ID = %s)"
        data = (user1_id, user2_id,)
        query = statement, data
        self.query_database(query)

        are_friends = self.cursor.rowcount != 0

        self.disconnect()
        return are_friends

    def check_friend_request(self, user_id_from, user_id_to):
        self.connect()

        statement = "SELECT * FROM FRIEND_REQUESTS WHERE (USER_ID_FROM = %s) AND (USER_ID_TO = %s)"
        data = (user_id_from, user_id_to,)
        query = statement, data
        self.query_database(query)

        already_sent = self.cursor.rowcount != 0

        self.disconnect()
        return already_sent
