from .deck import Deck
from .player import Player
from .evaluator import evaluate_winner

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
        self.action_history = []
        self.round_complete = False
        self.active_players = []
        self.last_aggressor = None

    def deal_player_cards(self):
        for p in self.players:
            p.hand = self.deck.deal(2)
    
    def advance_turn(self):
        # Go to next active player
        num_players = len(self.players)
        for i in range(1, num_players + 1):
            next_index = (self.turn_index + i) % num_players
            if not self.players[next_index].folded and self.players[next_index].chips > 0:
                self.turn_index = next_index
                return True
        return False
            
    def handle_player_action(self, action, amount=0):
        player = self.players[self.turn_index]
        result = {"status": "error", "message": "Invalid action"}

        # Record this action
        self.action_history.append({
            "player": player.name,
            "action": action,
            "amount": amount,
            "stage": self.stage
        })

        if action == "fold":
            player.folded = True
            result = {"status": "folded", "player": player.name}
            
            # Check if only one player remains
            active_players = [p for p in self.players if not p.folded]
            if len(active_players) == 1:
                self.stage = "showdown"  # Force showdown with 1 player
            
        elif action == "check":
            if player.current_bet == self.current_bet:
                result = {"status": "checked", "player": player.name}
            else:
                return {"status": "error", "message": "Cannot check. Must call or raise."}

        elif action == "call":
            to_call = self.current_bet - player.current_bet
            if to_call <= player.chips:
                self.pot += to_call
                player.chips -= to_call
                player.current_bet = self.current_bet
                result = {"status": "called", "amount": to_call, "pot": self.pot}
            else:
                # All-in call
                self.pot += player.chips
                player.current_bet += player.chips
                player.chips = 0
                result = {"status": "all-in call", "amount": player.chips, "pot": self.pot}

        elif action == "bet" or action == "raise":
            min_raise = self.current_bet * 2
            
            # Handle minimum bet in preflop
            if self.stage == "preflop" and self.current_bet == self.big_blind:
                min_raise = self.big_blind * 2
                
            if amount < min_raise and amount != player.chips:
                return {"status": "error", "message": f"Minimum raise is {min_raise}"}
                
            if amount <= player.chips:
                # How much more the player needs to add
                additional = amount - player.current_bet
                
                self.pot += additional
                player.chips -= additional
                player.current_bet = amount
                self.current_bet = amount
                self.last_aggressor = self.turn_index
                
                result = {"status": "bet", "amount": additional, "pot": self.pot}
            else:
                return {"status": "error", "message": "Not enough chips"}
        
        # Check if the round is complete
        self.check_round_completion()
        
        # Advance to next player if round not complete
        if not self.round_complete:
            self.advance_turn()
        
        return result
    
    def check_round_completion(self):
        """Check if betting round is complete"""
        active_players = [p for p in self.players if not p.folded]
        self.active_players = active_players
        
        # If only one player remains, round is complete
        if len(active_players) == 1:
            self.round_complete = True
            return
            
        # Round is complete when all active players have either:
        # 1. Called the current bet
        # 2. Gone all-in with fewer chips than the current bet
        for p in active_players:
            if p.chips > 0 and p.current_bet < self.current_bet:
                # Someone still needs to act
                self.round_complete = False
                return
        
        # If we make it here with multiple active players,
        # everyone has called or is all-in
        self.round_complete = True
    
    def make_bot_move(self):
        bot = self.players[self.turn_index]
        if not bot.is_bot:
            return {"status": "not a bot"}
        
        # Improved bot strategy based on stage and hand
        to_call = self.current_bet - bot.current_bet
        
        # Basic strategy based on shown cards and stage
        if self.stage == "preflop":
            if to_call == 0:  # Can check
                return self.handle_player_action("check", 0)
            elif to_call <= bot.chips // 4:  # Call if affordable
                return self.handle_player_action("call", 0)
            else:
                return self.handle_player_action("fold", 0)
        else:
            # Post-flop strategy
            if to_call == 0:
                if self.stage == "river" and len(self.active_players) > 1:
                    # Sometimes bet on river
                    import random
                    if random.random() < 0.3:
                        bet_amount = min(self.pot // 2, bot.chips)
                        return self.handle_player_action("bet", bot.current_bet + bet_amount)
                return self.handle_player_action("check", 0)
            elif to_call <= bot.chips // 3:
                return self.handle_player_action("call", 0)
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
            "round_complete": self.round_complete,
            "last_winner": getattr(self, "last_winner", None),
            "players": [
                {
                    "name": p.name,
                    "chips": p.chips,
                    "hand": serialize_hand(p.hand, p.is_bot),
                    "folded": p.folded,
                    "current_bet": p.current_bet,
                    "is_turn": self.turn_index == i,
                    "is_dealer": self.dealer_index == i
                }
                for i, p in enumerate(self.players)
            ]
        }
            
    def deal_flop(self):
        # Burn a card and deal 3
        self.deck.deal(1) 
        self.shown_cards += self.deck.deal(3)
        
    def deal_turn_river(self):
        self.deck.deal(1) 
        self.shown_cards += self.deck.deal(1)
        
    def start_new_betting_round(self):
        """Reset for a new betting round"""
        # Reset bets but keep the pot
        for p in self.players:
            p.current_bet = 0
        
        self.current_bet = 0
        self.round_complete = False
        
        # First player after dealer who is still in hand
        if len(self.players) == 2:  # Heads up
            # In heads-up, dealer acts first post-flop
            self.turn_index = self.dealer_index
        else:
            # Find first active player after dealer
            for i in range(1, len(self.players)):
                check_index = (self.dealer_index + i) % len(self.players)
                if not self.players[check_index].folded:
                    self.turn_index = check_index
                    break
        
        # Allow everyone to check or bet in this new round
        return {"status": "new_betting_round", "stage": self.stage}
    
    def advance_stage(self):
        """Progress to the next stage of the hand"""
        
        # If only one player left, skip to showdown
        active_players = [p for p in self.players if not p.folded]
        if len(active_players) == 1:
            self.stage = "showdown"
            return {"status": "showdown", "reason": "only_one_player"}
        
        if self.stage == "preflop":
            self.deal_flop()
            self.stage = "flop"
        elif self.stage == "flop":
            self.deal_turn_river()
            self.stage = "turn"
        elif self.stage == "turn":
            self.deal_turn_river()
            self.stage = "river"
        elif self.stage == "river":
            self.stage = "showdown"
        
        # Set up the new betting round
        result = self.start_new_betting_round()
        result["community_cards"] = [str(card) for card in self.shown_cards]
        return result
            
    def award_pot(self):
        active_players = [p for p in self.players if not p.folded]

        if len(active_players) == 1:
            winner = active_players[0]
            winner.chips += self.pot
            awarded = self.pot
            self.last_winner = winner.name
            self.pot = 0
            return {
                "winner": winner.name,
                "reason": "all_folded",
                "chips_won": awarded
            }

        # Evaluate showdown
        winners = evaluate_winner(active_players, self.shown_cards)
        share = self.pot // len(winners)

        for winner in winners:
            winner.chips += share

        self.last_winner = ", ".join(w.name for w in winners)
        awarded = self.pot
        self.pot = 0

        return {
            "winner": self.last_winner,
            "reason": "showdown",
            "chips_won": awarded
        }
        
    def reset(self):
        self.deck = Deck()
        self.pot = 0
        self.shown_cards = []
        self.stage = "preflop"
        self.round_complete = False
        self.action_history = []

        # Rotate dealer (in 2-player this alternates)
        self.dealer_index = (self.dealer_index + 1) % len(self.players)

        for p in self.players:
            p.hand = []
            p.folded = False
            p.current_bet = 0

        self.deal_player_cards()

        # Set up preflop betting with blinds
        sb_index = (self.dealer_index + 1) % len(self.players)
        bb_index = (self.dealer_index + 2) % len(self.players)
        
        # In heads-up (2 players), dealer posts SB and other player posts BB
        if len(self.players) == 2:
            sb_index = self.dealer_index
            bb_index = (self.dealer_index + 1) % 2

        small_blind_player = self.players[sb_index]
        big_blind_player = self.players[bb_index]

        # Post blinds
        small_blind_player.chips -= self.small_blind
        small_blind_player.current_bet = self.small_blind
        self.pot += self.small_blind

        big_blind_player.chips -= self.big_blind
        big_blind_player.current_bet = self.big_blind
        self.pot += self.big_blind

        self.current_bet = self.big_blind
        
        # First to act preflop is after BB
        self.turn_index = (bb_index + 1) % len(self.players)
        
        # In heads-up (2 players), dealer (SB) acts first preflop
        if len(self.players) == 2:
            self.turn_index = self.dealer_index

        # Make sure first player is active
        if self.players[self.turn_index].folded:
            self.advance_turn()