class Friend:
    def __init__(self, user1_id, user2_id, user2_name, date_befriended, is_blocked, num_of_shared_items,
                 num_of_shared_games, is_favourite):
        self.user1_id = user1_id
        self.user2_id = user2_id
        self.user2_name = user2_name
        self.date_befriended = date_befriended
        self.is_blocked = is_blocked
        self.num_of_shared_items = num_of_shared_items
        self.num_of_shared_games = num_of_shared_games
        self.is_favourite = is_favourite
