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
        self.stage = "preflop"
        self.small_blind = 25
        self.big_blind = 50
        self.dealer_index = 0  # rotates each hand

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
    
    def make_bot_move(self):
        bot = self.players[self.turn_index]
        if not bot.is_bot:
            return
        # Basic strategy: call current bet if possible
        to_call = self.current_bet - bot.current_bet
        if to_call <= bot.chips:
            return self.handle_player_action("bet", to_call)
        else:
            return self.handle_player_action("fold", 0)

    def get_state(self):
        def serialize_hand(hand, is_bot):
            if is_bot and self.stage != "showdown":
                return ["??", "??"]
            return [str(card) for card in hand]
        
        return {
            "pot": self.pot,
            "shown_cards": [str(card) for card in self.shown_cards],
            "turn_index": self.turn_index,
            "current_bet": self.current_bet,
            "stage": self.stage,
            "players": [
                {
                    "name": p.name,
                    "chips": p.chips,
                    "hand": serialize_hand(p.hand, p.is_bot),
                    "folded": p.folded,
                    "current_bet": p.current_bet
                }
                for p in self.players
            ]
        }

            
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
        self.stage = "preflop"
        for p in self.players:
            p.hand = []
            p.folded = False
            p.current_bet = 0