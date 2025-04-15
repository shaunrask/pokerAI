class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []
        self.chips = 100
        self.bet = 0
        self.folded = False

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
        self.bet += chips

    def fold(self):
        self.folded = True

    def reset(self):
        self.hand = []
