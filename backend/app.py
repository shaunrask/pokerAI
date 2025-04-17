from flask import Flask, request, jsonify
from flask_cors import CORS
from game.table import Table
from game.player import Player

app = Flask(__name__)
CORS(app)

def create_players(num_players=4):
    """Create a list of players with one human and the rest bots"""
    players = [Player("You", chips=1000)]
    
    # Add bots
    for i in range(1, num_players):
        players.append(Player(f"Bot{i}", is_bot=True, chips=1000))
    
    return players

# Initialize table with multiple players (default 4)
players = create_players(4)
table = Table(players)

# Add a new endpoint to get player positions
@app.route('/player_positions', methods=['GET'])
def get_player_positions():
    num_players = len(table.players)
    positions = []
    
    for i in range(num_players):
        # Calculate position around the table
        # 0 degrees is bottom center, moving clockwise
        angle = (360 / num_players * i - 90) % 360  # Start from bottom
        
        positions.append({
            "player": table.players[i].name,
            "angle": angle,
            "is_bot": table.players[i].is_bot,
            "seat": i
        })
    
    return jsonify(positions)

@app.route('/')
def home():
    return "Poker AI API is running!"

@app.route('/new_hand', methods=['POST'])
def new_hand():
    table.reset()
    
    # Get game state after reset
    state = table.get_state()
    
    # If first turn is a bot, make the bot move automatically
    bot_actions = []
    while table.players[table.turn_index].is_bot and not table.round_complete:
        bot_result = table.make_bot_move()
        bot_actions.append(bot_result)
    
    if bot_actions:
        state["bot_actions"] = bot_actions
    
    return jsonify(state)

@app.route('/player_action', methods=['POST'])
def player_action():
    data = request.get_json()
    action = data.get('action')  # e.g., "check", "call", "bet", "fold"
    amount = data.get('amount', 0)  # default to 0 if not provided
    
    # Handle player's action
    result = table.handle_player_action(action, amount)
    result["game_state"] = table.get_state()
    
    # Let bots take turns if it's their turn
    bot_actions = []
    while table.players[table.turn_index].is_bot and not table.round_complete:
        bot_result = table.make_bot_move()
        bot_actions.append(bot_result)
    
    if bot_actions:
        result["bot_actions"] = bot_actions
    
    # If betting round is complete, include that in result
    if table.round_complete:
        result["round_complete"] = True
        
        # If only one player remains, advance directly to showdown
        active_players = [p for p in table.players if not p.folded]
        if len(active_players) == 1:
            table.stage = "showdown"
            result["force_showdown"] = True
    
    return jsonify(result)

@app.route('/get_state', methods=['GET'])
def get_state():
    return jsonify(table.get_state())

@app.route('/next_stage', methods=['POST'])
def next_stage():
    # Only advance stage if the current betting round is complete
    if not table.round_complete and table.stage != "showdown":
        return jsonify({
            "status": "error",
            "message": "Cannot advance stage until betting round is complete"
        })
    
    # Handle showdown separately
    if table.stage == "showdown":
        winner_info = table.award_pot()
        # Include current chips for all players in response
        players_info = [{
            "name": p.name,
            "chips": p.chips
        } for p in table.players]
        return jsonify({
            "status": "game_over",
            "winner": winner_info,
            "players": players_info
        })
    
    # Advance to next stage (flop, turn, river)
    result = table.advance_stage()
    
    # Let bots play if first to act
    bot_actions = []
    while table.players[table.turn_index].is_bot and not table.round_complete:
        bot_result = table.make_bot_move()
        bot_actions.append(bot_result)
    
    if bot_actions:
        result["bot_actions"] = bot_actions
    
    # Include full game state
    result["game_state"] = table.get_state()
    
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
