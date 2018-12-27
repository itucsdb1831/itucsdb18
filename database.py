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
from screenshot_comment import ScreenshotComment


class Database:
    """Class that includes the database query functions.
    """
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
        """Inserts a user into the table "USERS".
        
        :param User user_to_insert: User object to insert.
        """
        self.connect()

        statement = """INSERT INTO USERS (NAME, PASSWORD) VALUES (%s, %s)"""
        data = (user_to_insert.get_user_name(), user_to_insert.get_pw(),)
        query = statement, data
        self.query_database(query)

        self.disconnect()

    def query_user_name(self, user_name):
        """Selects all from the table "USERS" with the name user_name. Returns a User object for given user name if there is a row, returns None otherwise.
        
        :param str user_name: user name to select.
        """
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
        """Selects all from the table "USERS" with the user id user_id. Returns a User object for given userid if there is a row, returns None otherwise.
        
        :param int user_id: user id to select.
        """
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
        """Selects user id from the table "USERS" with the name user_name. Returns a User object for given user name if there is a row, returns None otherwise.
        
        :param str user_name: user name to select.
        """
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
    
        
    def delete_user(self, user_id):
        """Deletes all from the table "USERS" with the id user_id.

        :param int user_id: user id to delete.
        """
        self.connect()

        statement = "DELETE FROM USERS WHERE USER_ID=%s"
        data = (user_id,)
        query = statement, data
        self.query_database(query)

        self.disconnect()

    def update_users_review_count_for_game(self, user_id, game_id, operation):
        if operation == "ADD":
            statement = "UPDATE GAMES_OF_USERS" \
                        + " SET NUM_OF_REVIEWS = NUM_OF_REVIEWS + 1" \
                        + " WHERE (USER_ID = %s) AND (GAME_ID = %s)"
        elif operation == "DELETE":
            statement = "UPDATE GAMES_OF_USERS" \
                        + " SET NUM_OF_REVIEWS = NUM_OF_REVIEWS - 1" \
                        + " WHERE (USER_ID = %s) AND (GAME_ID = %s)"

        data = (user_id, game_id)
        query = statement, data
        self.query_database(query)

    def insert_review(self, review):
        """Inserts a review into the table "REVIEWS".
        
        :param Review review: Review object to insert.
        """
        self.connect()

        self.update_users_review_count_for_game(review.user_id, review.game_id, "ADD")

        statement = """INSERT INTO REVIEWS (USER_ID, GAME_ID, LABEL, CONTENT, ADDED) VALUES (%s, %s, %s, %s, %s)"""
        data = (review.user_id, review.game_id, review.label, review.content, review.added,)
        query = statement, data
        self.query_database(query)

        self.disconnect()
    
    def get_reviews_of_user(self, user_id, cur_user_id):
        """Selects all from the table "REVIEWS" and also the related game titles with the user id user_id. Checks each review if the user with the user id cur_user_id liked or disliked it. Returns a list of Review objects in descending order according to the addition time.
        
        :param int user_id: user id to select.
        :param int cur_user_id: user id to check like/dislike situations.
        """
        self.connect()

        statement = """SELECT REVIEW_ID, REVIEWS.GAME_ID, LABEL, CONTENT, ADDED, LIKES, DISLIKES, UPDATED, TITLE FROM (REVIEWS JOIN GAMES ON ((REVIEWS.GAME_ID=GAMES.GAME_ID) AND (REVIEWS.USER_ID=%s))) ORDER BY ADDED DESC"""
        data = (user_id,)
        query = statement, data
        self.query_database(query)

        reviews = []
        for row in self.cursor:
            review_id, game_id, label, content, added, likes, dislikes, edited, game_title = row
            reviews.append(Review(user_id, game_id, label, added, content, likes, dislikes, edited, review_id, game_title))

        for review in reviews:
            review.liked_from_current = self.get_like_of_user(review.id, cur_user_id, "REVIEWS")
            review.disliked_from_current = self.get_dislike_of_user(review.id, cur_user_id, "REVIEWS")
        self.disconnect()
        return reviews

    def get_reviews_of_game(self, game_id, cur_user_id):
        """Selects all from the table "REVIEWS" and also the related user name with the game id game_id. Checks each review if the user with the user id cur_user_id liked or disliked it. Returns a list of Review objects in descending order according to the addition time.
        
        :param int game_id: game id to select.
        :param int cur_user_id: user id to check like/dislike situations.
        """
        self.connect()

        statement = """SELECT REVIEW_ID, REVIEWS.USER_ID, LABEL, CONTENT, ADDED, LIKES, DISLIKES, UPDATED, NAME FROM (REVIEWS JOIN USERS ON ((REVIEWS.USER_ID=USERS.USER_ID) AND (REVIEWS.GAME_ID=%s))) ORDER BY ADDED DESC"""
        data = (game_id,)
        query = statement, data
        self.query_database(query)

        reviews = []
        for row in self.cursor:
            review_id, user_id, label, content, added, likes, dislikes, edited, name = row
            reviews.append(Review(user_id, game_id, label, added, content, likes, dislikes, edited, review_id, None, name))

        for review in reviews:
            review.liked_from_current = self.get_like_of_user(review.id, cur_user_id, "REVIEWS")
            review.disliked_from_current = self.get_dislike_of_user(review.id, cur_user_id, "REVIEWS")
        self.disconnect()
        return reviews
    
    def get_prev_review(self, game_id, user_id):
        """Selects all from the table "REVIEWS" with the game id game_id and user id user_id. Returns a list of Review objects. Intuitively list may have 1 object at most.
        
        :param int game_id: game id to select.
        :param int user_id: user id to select.
        """
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
        """Updates reviews with review id review_id.
        
        :param int review_id: review id to update.
        """
        self.connect()

        statement = """UPDATE REVIEWS SET CONTENT=%s, LABEL=%s, UPDATED=%s WHERE REVIEW_ID=%s"""
        data = (content, label, edited, review_id,)
        query = statement, data
        self.query_database(query)
        
        self.disconnect()

    def get_review(self, review_id):
        """Selects all from the table "REVIEWS" with the review id review_id. Returns a Review object for given review id if there is a row, returns None otherwise.
        
        :param int review_id: review id to select.
        """
        self.connect()

        statement = "SELECT * FROM REVIEWS WHERE REVIEW_ID = %s"
        data = [review_id]
        query = statement, data
        self.query_database(query)

        review = None
        if self.cursor.rowcount != 0:
            user_id, game_id, label, content, likes, dislikes, id, added, edited = self.cursor.fetchone()
            review = Review(user_id, game_id, label, content, likes, dislikes, id, added, edited)

        self.disconnect()

        return review
    
    def delete_review(self, review_id):
        """Deletes all rows from the table "REVIEWS" with the review id review_id. Also deletes the related rows from the tables "LIKES" and "DISLIKES".
        
        :param int review_id: review id to delete.
        """
        review = self.get_review(review_id)
        self.update_users_review_count_for_game(review.user_id, review.game_id, "DELETE")  # *** BUGGED ***

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
        """Inserts a row into the table "LIKES" with given values.
        
        :param int user_id: User id that references the table "USERS".
        :param str entity_type: Entity type may be either "REVIEWS" or "SCREENSHOTS".
        :param int entity_id: Id that references the table given in the entity_type.
        """
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
        """Deletes a row from the table "LIKES" with given values.
        
        :param int user_id: User id that references the table "USERS".
        :param str entity_type: Entity type may be either "REVIEWS" or "SCREENSHOTS".
        :param int entity_id: Id that references the table given in the entity_type.
        """
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
        """Selects all from the table "LIKES" with the given values. Returns True if there is a row, returns False otherwise.
        
        :param int user_id: User id that references the table "USERS".
        :param str entity_type: Entity type may be either "REVIEWS" or "SCREENSHOTS".
        :param int entity_id: Id that references the table given in the entity_type.
        """
        self.connect()
        statement = """SELECT * FROM LIKES WHERE ((ENTITY_ID=%s) AND (USER_ID=%s) AND (ENTITY_TYPE=%s))"""
        data = (entity_id, user_id, entity_type,)
        query = statement, data
        self.query_database(query)
        
        is_liked = self.cursor.rowcount != 0
        self.disconnect()
        return is_liked
    
    def add_dislike(self, entity_id, user_id, entity_type):
        """Inserts a row into the table "DISLIKES" with given values.
        
        :param int user_id: User id that references the table "USERS".
        :param str entity_type: Entity type may be either "REVIEWS" or "SCREENSHOTS".
        :param int entity_id: Id that references the table given in the entity_type.
        """
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
        """Deletes a row from the table "DISLIKES" with given values.
        
        :param int user_id: User id that references the table "USERS".
        :param str entity_type: Entity type may be either "REVIEWS" or "SCREENSHOTS".
        :param int entity_id: Id that references the table given in the entity_type.
        """
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
        """Selects all from the table "DISLIKES" with the given values. Returns True if there is a row, returns False otherwise.
        
        :param int user_id: User id that references the table "USERS".
        :param str entity_type: Entity type may be either "REVIEWS" or "SCREENSHOTS".
        :param int entity_id: Id that references the table given in the entity_type.
        """
        self.connect()
        statement = """SELECT * FROM DISLIKES WHERE ((ENTITY_ID=%s) AND (USER_ID=%s) AND (ENTITY_TYPE=%s))"""
        data = (entity_id, user_id, entity_type,)
        query = statement, data
        self.query_database(query)
        is_disliked = self.cursor.rowcount != 0

        self.disconnect()
        return is_disliked

    def initialize_profile_photo(self, user_id):
        """
        When the user is created, initializes the profile photo to null which will be changed when the user uploads
        a photo.

        :type user_id: serial
        :param user_id: id of the user
        :return:
        """
        self.connect()

        statement = "INSERT INTO PROFILE_PHOTOS (USER_ID) VALUES (%s)"
        data = [user_id]
        query = statement, data
        self.query_database(query)

        self.disconnect()

    def change_profile_photo(self, profile_photo):
        """
        Changes the profile photo of the user.

        :type profile_photo: ProfilePhoto object
        :param profile_photo: all of the data about the photo uploaded by the user
        :return:
        """
        self.connect()

        statement = "UPDATE PROFILE_PHOTOS" \
                    + " SET NAME = %s" \
                    + " WHERE USER_ID = %s"
        data = (profile_photo.name, profile_photo.user_id)
        query = statement, data
        self.query_database(query)

        self.disconnect()

    def get_profile_photo_of_user(self, user_id):
        """
        Returns the name of the profile photo of the user.

        :type user_id: serial
        :param user_id: id of the user
        :return:
        """
        self.connect()

        statement = "SELECT NAME FROM PROFILE_PHOTOS WHERE USER_ID = %s"
        data = [user_id]
        query = statement, data
        self.query_database(query)

        profile_photo_name = None
        if self.cursor.rowcount != 0:
            profile_photo_name = self.cursor.fetchone()[0]

        self.disconnect()
        return profile_photo_name
    
    def insert_screenshot(self, ss):
        """Inserts a screenshot into the table "SCREENSHOTS".
        
        :param Screenshot ss: Screenshot object to insert.
        """
        self.connect()

        statement = "INSERT INTO SCREENSHOTS (NAME, USER_ID, GAME_ID, CAPTION, DATE_ADDED, LIKES, DISLIKES) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        data = (ss.name, ss.user_id, ss.game_id, ss.caption, ss.date_added, ss.likes, ss.dislikes,)
        query = statement, data
        self.query_database(query)
        self.disconnect()
    
    def get_screenshots_of_user(self, user_id, cur_user_id):
        """Selects all from the table "SCREENSHOTS" and also the related game titles with the user id user_id. Checks each screenshot if the user with the user id cur_user_id liked or disliked it. Returns a list of Screenshot objects in descending order according to the addition time.
        
        :param int user_id: user id to select.
        :param int cur_user_id: user id to check like/dislike situations.
        """
        self.connect()

        statement = "SELECT NAME, SCREENSHOTS.GAME_ID, CAPTION, DATE_ADDED, LIKES, DISLIKES, SHOT_ID, TITLE FROM (SCREENSHOTS JOIN GAMES ON ((SCREENSHOTS.GAME_ID=GAMES.GAME_ID) AND (SCREENSHOTS.USER_ID=%s))) ORDER BY DATE_ADDED DESC"
        data = (str(user_id),)
        query = statement, data
        self.query_database(query)
        sss = []
        for row in self.cursor:
            name, game_id, caption, date_added, likes, dislikes, shot_id, game_title = row
            sss.append(Screenshot(name, user_id, game_id, caption, date_added, likes, dislikes, shot_id, game_title))
        
        for shot in sss:
            shot.liked_from_current = self.get_like_of_user(shot.id, cur_user_id, "SCREENSHOTS")
            shot.disliked_from_current = self.get_dislike_of_user(shot.id, cur_user_id, "SCREENSHOTS")
        self.disconnect()
        return sss
    
    def get_screenshots_of_game(self, game_id, cur_user_id):
        """Selects all from the table "SCREENSHOTS" and also the related user names with the game id game_id. Checks each screenshot if the user with the user id cur_user_id liked or disliked it. Returns a list of Screenshot objects in descending order according to the addition time.
        
        :param int game_id: game id to select.
        :param int cur_user_id: user id to check like/dislike situations.
        """
        self.connect()
        statement = "SELECT SCREENSHOTS.NAME, SCREENSHOTS.GAME_ID, CAPTION, DATE_ADDED, LIKES, DISLIKES, SHOT_ID, USERS.NAME FROM (SCREENSHOTS JOIN USERS ON ((SCREENSHOTS.USER_ID=USERS.USER_ID) AND (SCREENSHOTS.GAME_ID=%s))) ORDER BY DATE_ADDED DESC"
        data = (str(game_id),)
        query = statement, data
        self.query_database(query)
        sss = []
        for row in self.cursor:
            name, user_id, caption, date_added, likes, dislikes, shot_id, user_name = row
            sss.append(Screenshot(name, user_id, game_id, caption, date_added, likes, dislikes, shot_id, None, user_name))
        
        for shot in sss:
            shot.liked_from_current = self.get_like_of_user(shot.id, cur_user_id, "SCREENSHOTS")
            shot.disliked_from_current = self.get_dislike_of_user(shot.id, cur_user_id, "SCREENSHOTS")
        self.disconnect()
        return sss
    
    def get_screenshot(self, shot_id):
        """Selects all from the table "SCREENSHOTS" with the shot id shot_id. Returns a Screenshot object for given shot id.
        
        :param int shot_id: shot id to select.
        """
        self.connect()

        statement = "SELECT SCREENSHOTS.NAME, SCREENSHOTS.USER_ID, CAPTION, DATE_ADDED, LIKES, DISLIKES, SCREENSHOTS.GAME_ID, GAMES.TITLE, USERS.NAME FROM (USERS JOIN (SCREENSHOTS JOIN GAMES ON SCREENSHOTS.GAME_ID=GAMES.GAME_ID) ON USERS.USER_ID=SCREENSHOTS.USER_ID) WHERE SHOT_ID=%s"
        data = (str(shot_id),)
        query = statement, data
        self.query_database(query)
        name, user_id, caption, date_added, likes, dislikes, game_id, game_title, user_name = self.cursor.fetchone()
        shot = Screenshot(name, user_id, game_id, caption, date_added, likes, dislikes, shot_id, game_title, user_name)
        self.disconnect()

        return shot
    
    def delete_screenshot(self, shot_name):
        """Deletes all rows from the table "SCREENSHOTS" with the shot id shot_id.
        
        :param int review_id: review id to delete.
        """
        self.connect()

        statement = "DELETE FROM SCREENSHOTS WHERE NAME=%s"
        data = (shot_name,)
        query = statement, data
        self.query_database(query)

        self.disconnect()

    # -------------------------------------------------------

    def add_game(self, game):
        """
        Adds the game to the GAMES table.

        :type game: Game object
        :param game: all of the data about the game to be added
        :return:
        """
        self.connect()

        statement = "INSERT INTO GAMES (TITLE, GENRE, AGE_RESTRICTION, PRICE) VALUES (%s, %s, %s, %s)"
        data = (game.title, game.genre, game.age_restriction, game.price,)
        query = statement, data
        self.query_database(query)

        self.disconnect()

    def edit_game(self, game_id, new_genre, new_age_restriction, new_price):
        """
        Changes the game's info.

        :param game_id: id of the game to be changed
        :param new_genre: new genre of the game
        :param new_age_restriction: new age restriction of the game
        :param new_price: new price of the game
        :return:
        """
        game = self.get_game(game_id)

        self.connect()

        statement = "UPDATE GAMES" \
                    + " SET GENRE = %s, AGE_RESTRICTION = %s, PRICE = %s" \
                    + " WHERE GAME_ID = %s"

        new_genre_ = new_genre
        new_age_restriction_ = new_age_restriction
        new_price_ = new_price

        if new_genre == "":
            new_genre_ = game.genre
        if new_age_restriction == "":
            new_age_restriction_ = game.age_restriction
        if new_price == "":
            new_price_ = game.price

        data = (new_genre_, new_age_restriction_, new_price_, game_id)
        query = statement, data
        self.query_database(query)

        self.disconnect()

    def get_game(self, game_id):
        """
        Returns all of the data about the game.

        :param game_id: id of the game
        :return:
        """
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
        """
        Returns the list of every game in the database to be listed on the store.

        :return:
        """
        self.connect()

        statement = "SELECT * FROM GAMES"
        self.cursor.execute(statement)

        games = []
        for row in self.cursor:
            (game_id, title, genre, rating, votes, age_restriction, price) = row
            game_ = Game(game_id, title, genre, rating, votes, age_restriction, price)
            games.append(game_)
        return games

    def update_user_rating(self, game_id, user_id, new_rating):
        """
        Changes the user's existing rating on the game with the new one on the table RATING_VOTES.

        :param game_id: id of the game that is rated
        :param user_id: id of the user who rated
        :param new_rating: new rating by the user
        :return:
        """
        self.connect()

        statement = "UPDATE RATING_VOTES" \
                    + " SET VOTE = (%s)" \
                    + " WHERE (USER_ID = %s) AND (GAME_ID = %s)"
        data = (new_rating, user_id, game_id)
        query = statement, data
        self.query_database(query)

        self.disconnect()

    def add_user_rating(self, game_id, user_id, rating):
        """
        Adds the user's rating of the game to the table RATING_VOTES.

        :param game_id: id of the game that is rated
        :param user_id: id of the user who rated
        :param rating: rating by the user
        :return:
        """
        self.connect()

        statement = "INSERT INTO RATING_VOTES VALUES (%s, %s, %s)"
        data = (user_id, game_id, rating)
        query = statement, data
        self.query_database(query)

        self.disconnect()

    def update_rating_of_game(self, game_id, user_id, new_rating, already_rated):
        """
        Adds the user's rating to the total and if it is the user's first time voting, increments the vote counter,
        else keeps the vote counter the same.

        :param game_id: id of the game that is rated
        :param user_id: id of the user that rated
        :param new_rating: new rating by the user
        :param already_rated: if the user rated the game before or not
        :return:
        """
        self.connect()

        change_in_rating = new_rating
        if already_rated:
            previous_rating = self.get_user_rating(game_id, user_id)
            change_in_rating = int(new_rating) - previous_rating

            self.update_user_rating(game_id, user_id, new_rating)

            statement = "UPDATE GAMES" \
                        + " SET RATING = (RATING * VOTES + %s) / VOTES" \
                        + " WHERE (GAME_ID = %s)"
        else:
            self.add_user_rating(game_id, user_id, new_rating)

            statement = "UPDATE GAMES" \
                        + " SET RATING = (RATING * VOTES + %s) / (VOTES + 1)," \
                        + " VOTES = VOTES + 1" \
                        + " WHERE (GAME_ID = %s)"

        data = (change_in_rating, game_id,)
        query = statement, data
        self.query_database(query)

        self.disconnect()

    def get_user_rating(self, game_id, user_id):
        """
        Returns the rating of the user for the game.

        :param game_id: id of the game that is rated
        :param user_id: id of the user who rated
        :return:
        """
        self.connect()

        statement = "SELECT * FROM RATING_VOTES WHERE (USER_ID = %s) AND (GAME_ID = %s)"
        data = (user_id, game_id)
        query = statement, data
        self.query_database(query)

        user_rating = None
        if self.cursor.rowcount != 0:
            user_rating = self.cursor.fetchone()[2]

        self.disconnect()
        return user_rating

    def is_already_rated(self, user_id, game_id):
        """
        Returns whether the user rated the game before or not.
        :param user_id: id of the user
        :param game_id: id of the game
        :return:
        """
        self.connect()

        statement = "SELECT * FROM RATING_VOTES WHERE (USER_ID = %s) AND (GAME_ID = %s)"
        data = (user_id, game_id)
        query = statement, data
        self.query_database(query)

        already_rated = self.cursor.rowcount != 0

        self.disconnect()
        return already_rated

    def delete_game(self, game_id):
        """
        Deletes the game from the database.

        :param game_id: id of the game to be deleted
        :return:
        """
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
        """
        Adds the game to the user's library.

        :param game_id: id of the game to be added
        :param user_id: id of the user who purchased the game
        :return:
        """
        self.connect()

        statement = "SELECT * FROM GAMES_OF_USERS WHERE (GAME_ID = %s) AND (USER_ID = %s)"
        data = (game_id, user_id,)
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

    def remove_game_from_user(self, user_id, game_id):
        """
        Deletes the game from the user's library.

        :param user_id: id of the user who owns the game
        :param game_id: id of the game to be deleted
        :return:
        """
        self.connect()

        statement = "SELECT * FROM GAMES_OF_USERS WHERE (GAME_ID = %s) AND (USER_ID = %s)"
        data = (game_id, user_id,)
        query = statement, data
        self.query_database(query)

        user_has_game = self.cursor.rowcount != 0
        if user_has_game:
            statement = "DELETE FROM GAMES_OF_USERS WHERE (USER_ID = %s) AND (GAME_ID = %s)"
            data = (user_id, game_id)
            query = statement, data
            self.query_database(query)

        self.disconnect()

    def update_game_favourite_variable(self, user_id, game_id, operation):
        """
        Sets the game as a favourite of the user or resets it.

        :param user_id: id of the user
        :param game_id: id of the game
        :param operation: if the game is to be favourited or unfavourited
        :return:
        """
        self.connect()

        if operation == "ADD":
            statement = "UPDATE GAMES_OF_USERS" \
                        + " SET IS_FAVOURITE = TRUE" \
                        + " WHERE (USER_ID = %s) AND (GAME_ID = %s)"
        elif operation == "REMOVE":
            statement = "UPDATE GAMES_OF_USERS" \
                        + " SET IS_FAVOURITE = FALSE" \
                        + " WHERE (USER_ID = %s) AND (GAME_ID = %s)"

        data = (user_id, game_id)
        query = statement, data
        self.query_database(query)

        self.disconnect()

    def get_games_of_user(self, user_id):
        """
        Returns all of the games of the user.

        :param user_id: id of the user
        :return:
        """
        self.connect()

        statement = "SELECT * FROM GAMES_OF_USERS WHERE USER_ID = %s"
        data = [user_id]
        query = statement, data
        self.query_database(query)

        games = []
        for row in self.cursor:
            (user_id_, game_id, title, time_played, time_purchased, num_of_reviews, num_of_items, is_favourite) = row
            game = GameOfUser(user_id_, game_id, title, time_played, time_purchased, num_of_reviews, num_of_items,
                              is_favourite)
            games.append(game)

        self.disconnect()
        return games

    def get_num_of_shared_games(self, user1_id, user2_id):
        """
        Returns the number of games owned by both friends.

        :param user1_id: id of user 1
        :param user2_id: id of user 2
        :return:
        """
        self.connect()

        statement = "SELECT COUNT(*) FROM (" \
                    + "(SELECT DISTINCT TITLE FROM GAMES_OF_USERS WHERE USER_ID = %s)" \
                    + " INTERSECT" \
                    + " (SELECT DISTINCT TITLE FROM GAMES_OF_USERS WHERE USER_ID = %s)" \
                    + ") AS SHARED_GAME"
        data = (user1_id, user2_id)
        query = statement, data
        self.query_database(query)

        num_of_shared_games = self.cursor.fetchone()[0]

        self.disconnect()
        return num_of_shared_games

    def get_num_of_shared_items(self, user1_id, user2_id):
        """
        Returns the number of items owned by both friends.

        :param user1_id: id of user 1
        :param user2_id: id of user 2
        :return:
        """
        self.connect()

        statement = "SELECT COUNT(*) FROM (" \
                    + "(SELECT DISTINCT NAME FROM ITEMS_OF_USERS WHERE USER_ID = %s)" \
                    + " INTERSECT" \
                    + " (SELECT DISTINCT NAME FROM ITEMS_OF_USERS WHERE USER_ID = %s)" \
                    + ") AS SHARED_ITEM"
        data = (user1_id, user2_id)
        query = statement, data
        self.query_database(query)

        num_of_shared_items = self.cursor.fetchone()[0]

        self.disconnect()
        return num_of_shared_items

    def set_num_of_shared_games(self, user1_id, user2_id):
        """
        Sets the number of games owned by both friends.

        :param user1_id: id of user 1
        :param user2_id: id of user 2
        :return:
        """
        num_of_shared_games = self.get_num_of_shared_games(user1_id, user2_id)

        self.connect()

        statement = "UPDATE FRIENDS" \
                    + " SET NUM_OF_SHARED_GAMES = %s" \
                    + " WHERE (USER1_ID = %s) AND (USER2_ID = %s)"
        data = (num_of_shared_games, user1_id, user2_id)
        query = statement, data
        self.query_database(query)

        data = (num_of_shared_games, user2_id, user1_id)
        query = statement, data
        self.query_database(query)

        self.disconnect()

    def set_num_of_shared_items(self, user1_id, user2_id):
        """
        Sets the number of items owned by both friends.

        :param user1_id: id of user 1
        :param user2_id: id of user 2
        :return:
        """
        num_of_shared_items = self.get_num_of_shared_items(user1_id, user2_id)

        self.connect()

        statement = "UPDATE FRIENDS" \
                    + " SET NUM_OF_SHARED_ITEMS = %s" \
                    + " WHERE (USER1_ID = %s) AND (USER2_ID = %s)"
        data = (num_of_shared_items, user1_id, user2_id)
        query = statement, data
        self.query_database(query)

        data = (num_of_shared_items, user2_id, user1_id)
        query = statement, data
        self.query_database(query)

        self.disconnect()

    def set_num_of_shared_games_for_all_friends(self, user_id):
        """
        Sets the number of games owned by both friends, between every friend of the user and the user themselves.

        :param user_id: id of the user
        :return:
        """
        friends_of_user = self.get_friends(user_id)

        for friend in friends_of_user:
            self.set_num_of_shared_games(user_id, friend.user2_id)

    def set_num_of_shared_items_for_all_friends(self, user_id):
        """
        Sets the number of items owned by both friends, between every friend of the user and the user themselves.

        :param user_id: id of the user
        :return:
        """
        friends_of_user = self.get_friends(user_id)

        for friend in friends_of_user:
            self.set_num_of_shared_items(user_id, friend.user2_id)

    def increment_time_played(self, user_id, game_id):
        """
        Increments the play time of the game owned by the user.

        :param user_id: id of the user who owns the game
        :param game_id: id of the game
        :return:
        """
        self.connect()

        statement = "UPDATE GAMES_OF_USERS" \
                    + " SET TIME_PLAYED = TIME_PLAYED + 1" \
                    + " WHERE (USER_ID = %s) AND (GAME_ID = %s)"
        data = (user_id, game_id)
        query = statement, data
        self.query_database(query)

        self.disconnect()

    def check_code(self, code):
        """
        Returns whether the entered balance code is valid or not.

        :param code: balance code entered by the user
        :return:
        """
        self.connect()

        statement = "SELECT * FROM BALANCE_CODES WHERE CODE = %s"
        data = [code]
        query = statement, data
        self.query_database(query)

        is_valid = self.cursor.rowcount != 0

        self.disconnect()
        return is_valid

    def add_balance_to_user(self, user_id):
        """
        Adds 100$ to the user's balance.

        :param user_id: id of the user
        :return:
        """
        self.connect()

        statement = "UPDATE USERS" \
                    + " SET BALANCE = BALANCE + 100" \
                    + " WHERE (USER_ID = %s)"
        data = [user_id]
        query = statement, data
        self.query_database(query)

        self.disconnect()

    def decrease_balance_of_user(self, user_id, amount):
        """
        Subtracts the amount from the user's balance.

        :param user_id: id of the user
        :param amount: amount of money to be subtracted
        :return:
        """
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

    def update_item(self, item):
        self.connect()

        statement = """UPDATE ITEMS
                           SET PICTURE = %s, NAME = %s, ITEM_TYPE = %s, RARITY = %s, PRICE = %s
                           WHERE ITEM_ID = %s"""
        data = (item.picture, item.name, item.item_type, item.rarity, item.price, item.item_id)
        query = statement, data
        self.query_database(query)

        self.disconnect()

    def delete_item_from_user(self, item_id, user_id):
        self.connect()

        statement = """DELETE FROM ITEMS_OF_USERS
                           WHERE ITEM_ID = %s AND USER_ID = %s"""
        data = (item_id, user_id)
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

    def update_users_item_count_for_game(self, user_id, game_id, operation):
        statement = None
        if operation == "ADD":
            statement = "UPDATE GAMES_OF_USERS" \
                        + " SET NUM_OF_ITEMS = NUM_OF_ITEMS + 1" \
                        + " WHERE (USER_ID = %s) AND (GAME_ID = %s)"

        data = (user_id, game_id)
        query = statement, data
        self.query_database(query)

    def check_item_ownership(self, item_id, user_id):
        self.connect()

        statement = """SELECT * FROM ITEMS_OF_USERS WHERE (ITEM_ID = %s) AND USER_ID = %s"""
        data = (item_id, user_id)
        query = statement, data
        self.query_database(query)
        already_has_item = self.cursor.rowcount != 0

        self.disconnect()
        return already_has_item

    def add_item_to_user(self, item_id, game_id, user_id):
        self.connect()

        already_has_item = self.check_item_ownership(item_id, user_id)
        if already_has_item:
            statement = """UPDATE ITEMS_OF_USERS
                               SET LEVEL = LEVEL + 1
                               WHERE ITEM_ID = %s AND USER_ID = %s;"""
            data = (item_id, user_id)
            query = statement, data
            self.query_database(query)
        else:
            self.update_users_item_count_for_game(user_id, game_id, "ADD")

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

    # Screenshot Comments
    def get_screenshot_comments(self, game_id, screenshot_id):
        self.connect()

        statement = """SELECT * FROM SCREENSHOT_COMMENTS WHERE (GAME_ID = %s) AND (SCREENSHOT_ID = %s)"""
        data = [game_id, screenshot_id]
        query = statement, data
        self.query_database(query)

        screenshot_comments = []
        for row in self.cursor:
            (comment_id, user_id, game_id, screenshot_id, username, content,
                date_commented, reaction, likes, dislikes) = row
            comment = ScreenshotComment(comment_id, user_id, game_id, screenshot_id,
                                        username, content, date_commented, reaction, likes, dislikes)
            screenshot_comments.append(comment)

        self.disconnect()
        return screenshot_comments

    def add_screenshot_comment(self, user_id, game_id, screenshot_id, content, reaction, font_size, color):
        self.connect()

        statement = """INSERT INTO
                            SCREENSHOT_COMMENTS(USER_ID, GAME_ID, SCREENSHOT_ID, USERNAME,
                                CONTENT, DATE_COMMENTED, REACTION, FONT_SIZE, COLOR)
                            VALUES (%s, %s, %s, %s, %s, CURRENT_DATE, %s, %s, %s)"""
        username = self.get_user(user_id).user_name
        data = (user_id, game_id, screenshot_id, username, content, reaction, font_size, color)
        query = statement, data
        self.query_database(query)

        self.disconnect()

    def delete_screenshot_comment(self, comment_id):
        self.connect()

        statement = """DELETE FROM SCREENSHOT_COMMENTS WHERE COMMENT_ID = %s"""
        data = [comment_id]
        query = statement, data
        self.query_database(query)

        self.disconnect()

    def update_screenshot_comment(self, comment_id, user_id, game_id, screenshot_id, content, reaction, font_size, color):
        self.connect()

        statement = """UPDATE SCREENSHOT_COMMENTS
                           SET CONTENT = %s, DATE_COMMENTED = CURRENT_DATE,
                               REACTION = %s, FONT_SIZE = %s, COLOR = %s
                           WHERE (COMMENT_ID = %s) AND (GAME_ID = %s) AND (USER_ID = %s) AND (SCREENSHOT_ID = %s)"""
        data = (content, reaction, font_size, color,
                comment_id, game_id, user_id, screenshot_id)
        query = statement, data
        self.query_database(query)

        self.disconnect()

    # -------------------------------------------------------

    def send_friend_request(self, user_id_from, user_id_to):
        """
        Adds the friend request to the database.

        :param user_id_from: id of the user who sent the request
        :param user_id_to: id of the user who received the request
        :return:
        """
        user_name_from = self.get_user(user_id_from).user_name
        user_name_to = self.get_user(user_id_to).user_name
        self.connect()

        statement = "INSERT INTO FRIEND_REQUESTS VALUES(%s, %s, %s, %s)"
        data = (user_id_from, user_id_to, user_name_from, user_name_to)
        query = statement, data
        self.query_database(query)

        self.disconnect()

    def add_friend(self, user1_id, user2_id):
        """
        Adds the users as friends to the database.

        :param user1_id: id of user 1
        :param user2_id: id of user 2
        :return:
        """
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
        """
        Returns every friend request sent to the user.

        :param user_id_to: id of the user
        :return:
        """
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
        """
        Returns every friend request sent by the user.

        :param user_id_from: id of the user
        :return:
        """
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
        """
        Removes the sent friend request from the database.

        :param user_id_from: id of the user who sent the request
        :param user_id_to: id of the user who received the request
        :return:
        """
        self.connect()

        statement = "DELETE FROM FRIEND_REQUESTS WHERE (USER_ID_FROM = %s) AND (USER_ID_TO = %s)"
        data = (user_id_from, user_id_to,)
        query = statement, data
        self.query_database(query)

        self.disconnect()

    def get_friends(self, user_id):
        """
        Returns the list of the friends of the user.

        :param user_id: id of the user
        :return:
        """
        self.connect()

        statement = "SELECT * FROM FRIENDS WHERE USER1_ID = %s"
        data = [user_id]
        query = statement, data
        self.query_database(query)

        friends = []
        for row in self.cursor:
            (user1_id, user2_id, user2_name, date_befriended, is_blocked, num_of_shared_items,
             num_of_shared_games, is_favourite) = row
            friend = Friend(user1_id, user2_id, user2_name, date_befriended, is_blocked, num_of_shared_items,
                            num_of_shared_games, is_favourite)
            friends.append(friend)

        self.disconnect()
        return friends

    def check_if_already_friends(self, user1_id, user2_id):
        """
        Returns whether the users are already friends or not.

        :param user1_id: id of user 1
        :param user2_id: id of user 2
        :return:
        """
        self.connect()

        statement = "SELECT * FROM FRIENDS WHERE (USER1_ID = %s) AND (USER2_ID = %s)"
        data = (user1_id, user2_id,)
        query = statement, data
        self.query_database(query)

        are_friends = self.cursor.rowcount != 0

        self.disconnect()
        return are_friends

    def check_friend_request(self, user_id_from, user_id_to):
        """
        Returns if the user already sent the friend request to the other user.

        :param user_id_from: id of the user who sent the request
        :param user_id_to: id of the user who received the request
        :return:
        """
        self.connect()

        statement = "SELECT * FROM FRIEND_REQUESTS WHERE (USER_ID_FROM = %s) AND (USER_ID_TO = %s)"
        data = (user_id_from, user_id_to,)
        query = statement, data
        self.query_database(query)

        already_sent = self.cursor.rowcount != 0

        self.disconnect()
        return already_sent
      
    def get_all_reviews_of_user_for_community(self, user_id):
        """
        Returns the list of reviews made by the user to be displayed on the community page.

        :param user_id: id of the user
        :return:
        """
        self.connect()

        statement = "SELECT USER_ID, GAME_ID, CONTENT, ADDED FROM REVIEWS WHERE USER_ID = %s"
        data = [user_id]
        query = statement, data
        self.query_database(query)

        reviews = []
        for row in self.cursor:
            (user_id_, game_id, content, timestamp) = row
            user_name = self.get_user(user_id_).user_name
            game_title = self.get_game(game_id).title
            reviews.append((user_name, game_title, content, timestamp))

        self.disconnect()
        return reviews

    def get_all_screenshots_of_user_for_community(self, user_id):
        """
        Returns the list of screenshots uploaded by the user to be displayed on the community page.

        :param user_id: id of the user
        :return:
        """
        self.connect()

        statement = "SELECT NAME, USER_ID, GAME_ID, DATE_ADDED FROM SCREENSHOTS WHERE USER_ID = %s"
        data = [user_id]
        query = statement, data
        self.query_database(query)

        screenshots = []
        for row in self.cursor:
            (name, user_id_, game_id, timestamp) = row
            user_name = self.get_user(user_id_).user_name
            game_title = self.get_game(game_id).title
            screenshots.append((name, user_name, game_title, timestamp))

        self.disconnect()
        return screenshots

    def get_all_not_blocked_friends_for_community(self, user_id):
        """
        Returns the list of friends of the user who are not blocked by the user.

        :param user_id: id of the user
        :return:
        """
        self.connect()

        statement = "SELECT USER2_ID FROM FRIENDS WHERE (USER1_ID = %s) AND (IS_BLOCKED = FALSE)"
        data = [user_id]
        query = statement, data
        self.query_database(query)

        not_blocked_friends = []
        for row in self.cursor:
            not_blocked_friends.append(row[0])

        self.disconnect()
        return not_blocked_friends

    def update_friend_variable(self, user1_id, user2_id, operation):
        """
        Handles the favourite/unfavourite, block/unblock and remove operations related to friends.

        :param user1_id: id of user 1
        :param user2_id: id of user 2
        :param operation: favourite/unfavourite, block/unblock or remove
        :return:
        """
        self.connect()

        response = None
        statement = None
        if operation == "BLOCK":
            response = "Blocked"
            statement = "UPDATE FRIENDS" \
                        + " SET IS_BLOCKED = TRUE" \
                        + " WHERE (USER1_ID = %s) AND (USER2_ID = %s)"
        elif operation == "UNBLOCK":
            response = "Unblocked"
            statement = "UPDATE FRIENDS" \
                        + " SET IS_BLOCKED = FALSE" \
                        + " WHERE (USER1_ID = %s) AND (USER2_ID = %s)"
        elif operation == "FAVOURITE":
            response = "Favourited"
            statement = "UPDATE FRIENDS" \
                        + " SET IS_FAVOURITE = TRUE" \
                        + " WHERE (USER1_ID = %s) AND (USER2_ID = %s)"
        elif operation == "UNFAVOURITE":
            response = "Unfavourited"
            statement = "UPDATE FRIENDS" \
                        + " SET IS_FAVOURITE = FALSE" \
                        + " WHERE (USER1_ID = %s) AND (USER2_ID = %s)"
        elif operation == "REMOVE":
            are_friends = self.check_if_already_friends(user1_id, user2_id)
            if are_friends:
                response = "Removed"
                statement = "DELETE FROM FRIENDS WHERE (USER1_ID = %s) AND (USER2_ID = %s)"

                data = (user2_id, user1_id)
                query = statement, data
                self.query_database(query)

                data = (user1_id, user2_id)
                query = statement, data
                self.query_database(query)

            return response

        data = (user1_id, user2_id)
        query = statement, data
        self.query_database(query)

        self.disconnect()
        return response

