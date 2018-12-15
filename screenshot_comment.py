class ScreenshotComment:
    def __init__(self, comment_id, user_id, game_id, screenshot_id,
                 username, content, date_commented, reaction, font_size, color):
        self.comment_id = comment_id
        self.user_id = user_id
        self.game_id = game_id
        self.screenshot_id = screenshot_id
        self.username = username
        self.content = content
        self.date_commented = date_commented
        self.reaction = reaction
        self.font_size = font_size
        self.color = color
