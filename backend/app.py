from flask import Flask, request, jsonify
from flask_cors import CORS
from game.table import Table
from game.player import Player

app = Flask(__name__)
CORS(app)

#Initialize table with 1 user and 1 bots
players = [Player("You"), Player("Bot1", is_bot=True)]
table = Table(players)

@app.route('/')
def home():
    return "Poker AI API is running!"

@app.route('/new_hand')
def new_hand():
    table.reset()
    table.deal_player_cards()
    return jsonify({
        "your_hand": [str(card) for card in players[0].hand],
    })

@app.route('/player_action', methods=['POST'])
def player_action():
    data = request.get_json()
    action = data.get('action')     # e.g., "check", "bet", "fold"
    amount = data.get('amount', 0)  # default to 0 if not provided

    result = table.handle_player_action(action, amount)
    
    # Let bots take turns if it's their turn
    while table.players[table.turn_index].is_bot:
        bot_result = table.make_bot_move()
        result["bot_action"] = bot_result

    return jsonify(result)

def make_bots_move(self):
    while table.players[table.turn_index].is_bot:
        bot_result = table.make_bot_move()
        
@app.route('/get_state', methods=['GET'])
def get_state():
    return jsonify(table.get_state())

@app.route('/next_stage', methods=['POST'])
def next_stage():
    if table.stage == "preflop":
        table.deal_flop()
        table.stage = "flop"
    elif table.stage == "flop":
        table.deal_turn_river()
        table.stage = "turn"
    elif table.stage == "turn":
        table.deal_turn_river()
        table.stage = "river"
    elif table.stage == "river":
        table.stage = "showdown"
        # Call your evaluator here once built

    return jsonify({
        "stage": table.stage,
        "shown_cards": [str(card) for card in table.shown_cards]
    })


if __name__ == "__main__":
    app.run(debug=True)