from treys import Card, Evaluator as TreysEvaluator

def convert_str_to_card(card_str):
    """
    Convert a card string to a treys Card object
    Input format: '2h', 'Ts', 'Kd', 'Ac', etc.
    """
    # Extract rank and suit
    rank = card_str[0].upper()
    suit = card_str[1].lower()
    
    # Full mapping for ranks and suits
    rank_map = {
        '2': '2', '3': '3', '4': '4', '5': '5', '6': '6', 
        '7': '7', '8': '8', '9': '9', 'T': 'T', 'J': 'J', 
        'Q': 'Q', 'K': 'K', 'A': 'A'
    }
    
    suit_map = {'s': 's', 'h': 'h', 'd': 'd', 'c': 'c'}
    
    # Format for treys
    card_code = f"{rank_map.get(rank, rank)}{suit_map.get(suit, suit)}"
    return Card.new(card_code.lower())

def evaluate_winner(players, community_cards):
    """
    Evaluate which player(s) have the winning hand
    Returns a list of winning Player objects
    """
    evaluator = TreysEvaluator()
    
    # Convert community cards to treys format
    treys_board = [convert_str_to_card(str(card)) for card in community_cards]
    
    active_players = [p for p in players if not p.folded]
    
    # If only one player remains, they win
    if len(active_players) == 1:
        return active_players
    
    best_score = float('inf')  # Lower is better in treys
    winners = []
    
    for player in active_players:
        # Convert player hand to treys format
        treys_hand = [convert_str_to_card(str(card)) for card in player.hand]
        
        # Evaluate hand strength
        score = evaluator.evaluate(treys_board, treys_hand)
        
        if score < best_score:
            best_score = score
            winners = [player]
        elif score == best_score:
            winners.append(player)
    
    return winners