class Review:
    def __init__(self, user_id, game_id, label, added, content="", likes=0, dislikes=0, edited = None, id=None, game_title=None):
        self.user_id = user_id
        self.game_id = game_id
        self.label = label
        self.content = content
        self.likes = likes
        self.dislikes = dislikes
        self.id=id
        self.added = added
        self.edited = edited
        self.game_title = game_title
