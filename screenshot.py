class Screenshot:
    def __init__(self, name, user_id, game_id, caption, date_added, likes=0, dislikes=0, id=0, game_title=None):
        self.name = name
        self.caption = caption
        self.date_added = date_added
        self.likes = likes
        self.dislikes = dislikes
        self.id = id
        self.user_id = user_id
        self.game_id = game_id
        self.game_title = game_title
