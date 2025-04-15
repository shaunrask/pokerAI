class Player:
    def __init__(self, name, is_bot = False):
        self.name = name
        self.hand = []
        self.chips = 1000
        self.current_bet = 0
        self.folded = False
        self.is_bot = is_bot

    def __str__(self):
        return f"{self.name} ({self.chips} chips)"

    def __repr__(self):
        return f"{self.name} ({self.chips} chips)"

    def add_chips(self, chips):
        self.chips += chips

    def remove_chips(self, chips):
        self.chips -= chips

    def bet_chips(self, chips):
        self.chips -= chips
        self.current_bet += chips

    def fold(self):
        self.folded = True

    def reset(self):
        self.hand = []
