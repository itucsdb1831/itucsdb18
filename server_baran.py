class Server:
    """
    Server
    """
    def __init__(self):
        pass

    def item_add_page(self, game_id):
        """
        Serves the item adding page for the admin and handles adding an item to the database.

        If the request method is "POST",
        then tries to create an instance of Item which will be added to the database and displays the result page,
        if any exception is raised, then refreshes the current page without any database operations.

        :param game_id: ID for the game that the item is to be added
        :return: Item adding page or the result page
        """

    def item_update_page(self, game_id, item_id):
        """
        Serves the item updating page for the admin and handles updating an item in the database.

        If the request method is "POST",
        then tries to create an instance of Item which will be used to update the database and displays the result page.
        if any exception is raised, then refreshes the current page without any database operations.

        :param game_id: ID of the game for which the item will be updated
        :param item_id: ID of the item to be updated
        :return: Item updating page or the result page
        """

    def item_purchase_page(self, game_id, item_id):
        """
        Serves the page for purchasing an item.

        :param game_id: ID of the game to which the item belongs
        :param item_id: ID of the item to be purchased
        :return: Item purchase page
        """

    def item_purchase_result_page(game_id, item_id):
        """
        Serves the resulting page after the user purchases (or levels up) an item.

        :param item_id: ID of the item purchased (or leveled up)
        :return: Item purchasing result page
        """

    def item_edit_page(self, item_id):
        """
        Serves the item editing page for admins.

        If the method is "POST",
        then gets item attributes from the request form and edits the item in the database according to those attributes
        and displays the result page.
        Otherwise, displays the item editing page.

        :param item_id: ID of the item to be edited
        :return: Editing page or result page
        """

    def item_edit_result_page(self):
        """
        Serves the result page for item editing.
        :return: Item edit result page
        """

    def screenshot_comment_edit_page(self, game_id, screenshot_id, comment_id):
        """
        Serves the comment editing page for a screenshot.

        If the method is "POST",
        then gets the attributes of the comment from the request form and updates the comment in the database and displays the result page.
        Otherwise, displays the comment editing page.

        :param game_id: ID of the game from where the screenshot is taken
        :param screenshot_id: ID of the screenshot for which the comment is made
        :param comment_id: ID of the comment.
        :return: Screenshot comment editing page or the result page
        """

    def screenshot_comment_edit_result_page(self, game_id, screenshot_id):
        """
        Serves the result of the comment editing page

        :param game_id: ID of the game from where the screenshot is taken
        :param screenshot_id: ID of the screenshot for which the comment is edited
        :return: Screenshot comment editing result page
        """
