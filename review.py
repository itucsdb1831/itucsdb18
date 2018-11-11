class Review:
    def __init__(self, user_id, game_id, label, content="", likes=0, dislikes=0, id=None):
        self.user_id = user_id
        self.game_id = game_id
        self.label = label
        self.content = content
        self.likes = 0
        self.dislikes = 0
        self.id=id