class Game:
    def __init__(self, game_id, title, genre, rating, votes, age_restriction, price):
        self.game_id = game_id
        self.title = title
        self.genre = genre
        self.rating = rating
        self.votes = votes
        self.age_restriction = age_restriction
        self.price = price