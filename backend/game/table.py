import deck

class Table:
    def __init__(self, players):
        self.players = players
        self.deck = deck.Deck()
        self.pot = 0
        self.shown_cards = []
        
    def deal_player_cards(self):
        for p in self.players:
            p.hand = self.deck.deal(2)
            
    def deal_flop(self):
        #Burn a card and deal 3
        self.deck.deal(1) 
        self.shown_cards += self.deck.deal(3)
        
    def deal_turn_river(self):
        self.deck.deal(1) 
        self.shown_cards += self.deck.deal(1)
        
    def reset(self):
        self.deck = deck.Deck()
        self.pot = 0
        self.shown_cards = []
        for p in self.players:
            p.hand = []
            p.folded = False
            p.current_bet = 0