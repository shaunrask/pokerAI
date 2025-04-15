class Player:
    def __init__(self, name, is_bot=False, chips=1000):
        self.name = name
        self.chips = chips
        self.hand = []
        self.folded = False
        self.current_bet = 0
        self.is_bot = is_bot
        
        # For better bot decision making
        self.playing_style = {
            'aggression': 0.5,  # 0 = passive, 1 = aggressive
            'tightness': 0.5,   # 0 = loose, 1 = tight
            'bluff_frequency': 0.2  # How often the bot bluffs
        }
        
        if is_bot:
            import random
            # Randomize bot playing styles
            self.playing_style['aggression'] = random.uniform(0.3, 0.7)
            self.playing_style['tightness'] = random.uniform(0.3, 0.7)
            self.playing_style['bluff_frequency'] = random.uniform(0.1, 0.3)
    
    def __str__(self):
        return f"{self.name} (Chips: {self.chips})"
    
    def calculate_hand_strength(self, community_cards=[]):
        """
        For bots - calculate a simple estimate of hand strength
        Returns value 0-1 where higher is better
        """
        if not self.hand:
            return 0
            
        # Simple pre-flop hand strength calculation
        if len(community_cards) == 0:
            # Check for pairs
            if self.hand[0][0] == self.hand[1][0]:
                # Pair value depends on rank
                rank = self.hand[0][0]
                if rank in ['A', 'K', 'Q', 'J', 'T']:
                    return 0.9  # High pair
                elif rank in ['9', '8', '7']:
                    return 0.8  # Medium pair
                else:
                    return 0.7  # Low pair
                    
            # Check for high cards
            high_cards = 0
            for card in self.hand:
                if card[0] in ['A', 'K', 'Q', 'J', 'T']:
                    high_cards += 1
                    
            # Check for suited cards
            suited = self.hand[0][1] == self.hand[1][1]
            
            # Calculate a basic hand strength
            if suited and high_cards == 2:
                return 0.8  # Suited high cards
            elif high_cards == 2:
                return 0.7  # Two high cards
            elif suited and high_cards == 1:
                return 0.6  # Suited with one high card
            elif high_cards == 1:
                return 0.5  # One high card
            elif suited:
                return 0.4  # Suited low cards
            else:
                return 0.3  # Unsuited low cards
        
        # If we have community cards, we'd do more sophisticated evaluation
        # This would use the treys evaluator but is simplified here
        return 0.5  # Default medium strength with community cards
        
    def should_fold(self, table_state):
        """Bot decision logic for folding"""
        if not self.is_bot:
            return False
            
        hand_strength = self.calculate_hand_strength(table_state.get('shown_cards', []))
        pot_odds = table_state.get('current_bet', 0) / table_state.get('pot', 1)
        
        # Fold threshold based on playing style and hand strength
        fold_threshold = self.playing_style['tightness'] - hand_strength
        
        # More likely to fold if the bet is large relative to the pot
        if pot_odds > 0.5:
            fold_threshold -= 0.2
            
        # Random factor for unpredictability
        import random
        if random.random() < fold_threshold:
            return True
            
        return False