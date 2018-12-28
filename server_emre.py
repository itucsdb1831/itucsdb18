class Server:
    """Server"""
    def __init__(self):
        self.empty = None

    def upload_profile_photo_page(self, user_id):  # Emre
        """
        Serves the page and handles the operation for uploading a profile photo by the user.

        :param user_id: id of the user
        :return: user's profile page
        """

    def store_page(self):  # Emre
        """
        Serves the page and handles the operation for viewing and deleting games.

        :return: the store page
        """

    def community_page(self):  # Emre
        """
        Serves the page for viewing the activities of unblocked friends.

        :return: the community page
        """

    def game_page(self, game_id):  # Emre
        """
        Serves game specific page and handles the operations for deleting items.

        :param game_id: id of the game
        :return: the game page
        """

    def game_add_page(self):  # Emre
        """
        Serves the game adding page for the admin and handles the operation for adding the game to the database.

        :return: not_allowed for non admins, game_add page or the result page
        """

    def game_edit_page(self, game_id):  # Emre
        """
        Serves the page for editing the game and handles the operations for editing the game.

        :param game_id: id of the game
        :return: game page or game_edit page
        """

    def game_add_page_result_page(self):  # Emre
        """
        Serves the pages for the result of adding a game.

        :return: not_allowed for non-admins or the result page
        """

    def game_rate_page(self, game_id):  # Emre
        """
        Serves the page and handles the operation for rating a game.

        :param game_id: id of the game
        :return: game rating page or the result page
        """

    def game_purchase_page(self, game_id):  # Emre
        """
        Serves the page and handles the operation for purchasing a game.

        :param game_id: id of the game
        :return: game purchase page
        """

    def game_purchase_result_page(self, game_id):  # Emre
        """
        Serves the page for the result of the purchasing of a game and handles the operations of decreasing the user's
        balance, adding the game to the user's account and setting thr number of shared games between the user and
        all of their friends.

        :param game_id: id of the game
        :return: the result page for purchasing the game
        """

    def code_enter_page(self):  # Emre
        """
        Serves the pages code_enter and the result and handles the operations of checking the validity of the
        code and adding the amount to the user's balance.

        :return: the code enter or the result page
        """

    def process_friend_request_response(self):  # Emre
        """
        Processes the response given to a friend request. If the user has accepted the request, adds them as friends
        to the database, removes the request to the database, and sets the number of shared games and items variables
        correctly. If the request was  or cancelled, removes the friend request from the database.

        :return: the result of the response as text
        """

    def friend_add_page(self):  # Emre
        """
        Serves the page for adding a friend and handles the operation of checking if the friend request is valid. The request is
        not valid if the users are already friends, if the user has sent a request to themselves or the user has already sent a
        request before which is still pending.

        :return: friend add page or the result page
        """

    def process_game_favouriting(self):  # Emre
        """
        Processes the operations of favouriting or unfavouriting a game.

        :return: the response text
        """

    def process_play_game(self):  # Emre
        """
        Processes the playing the game operation. Simply increments the play time by 1 hour.

        :return: the incremented play time
        """

    def process_friend_operations(self):  # Emre
        """
        Processes the operations related to friends, such as blocking, favouriting and removing the friend.

        :return: the response text
        """

    def process_remove_friend(self, user1_id, user2_id):  # Emre
        """
        Processes the removing friend operation.

        :param user1_id: id of the user 1
        :param user2_id: id of the user 2
        :return: the profile page
        """

    def process_drop_game(self, user_id, game_id):  # Emre
        """
        Processes the operation of user deleting a game from their library.
        
        :param user_id: id of the user
        :param game_id: id of the game
        :return: the profile page
        """