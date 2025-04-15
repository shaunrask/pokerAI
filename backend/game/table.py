from .deck import Deck
from .player import Player

class Table:
    def __init__(self, players):
        self.players = players
        self.deck = Deck()
        self.pot = 0
        self.shown_cards = []
        self.current_bet = 0
        self.turn_index = 0
        
    def deal_player_cards(self):
        for p in self.players:
            p.hand = self.deck.deal(2)
    
    def advance_turn(self):
        #Go to next active player
        num_players = len(self.players)
        for i in range(1, num_players + 1):
            next_index = (self.turn_index + i) % num_players
            if not self.players[next_index].folded:
                self.turn_index = next_index
                return
            
    def handle_player_action(self, action, amount):
        player = self.players[self.turn_index]

        if action == "fold":
            player.folded = True
            return {"status": "folded", "player": player.name}

        elif action == "check":
            if player.current_bet == self.current_bet:
                return {"status": "checked", "player": player.name}
            else:
                return {"status": "error", "message": "Cannot check. Must call or raise."}

        elif action == "bet":
            if amount <= player.chips and amount <= 2 * self.current_bet:
                self.pot += amount
                player.chips -= amount
                player.current_bet += amount
                self.current_bet = max(self.current_bet, player.current_bet)
                return {"status": "bet", "amount": amount, "pot": self.pot}
            else:
                return {"status": "error", "message": "Not enough chips"}

        return {"status": "error", "message": "Unknown action"}
            
    def deal_flop(self):
        #Burn a card and deal 3
        self.deck.deal(1) 
        self.shown_cards += self.deck.deal(3)
        
    def deal_turn_river(self):
        self.deck.deal(1) 
        self.shown_cards += self.deck.deal(1)
        
    def reset(self):
        self.deck = Deck()
        self.pot = 0
        self.shown_cards = []
        for p in self.players:
            p.hand = []
            p.folded = False
            p.current_bet = 0