from flask import Flask, request, jsonify
from game.table import Table
from game.player import Player

app = Flask(__name__)

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
        "your_hand": players[0].hand,
    })

@app.route('/player_action', methods=['POST'])
def player_action():
    data = request.get_json()
    action = data.get('action')     # e.g., "check", "bet", "fold"
    amount = data.get('amount', 0)  # default to 0 if not provided

    result = Table.handle_player_action(action, amount)

    return jsonify(result)

def make_bot_move(self):
    bot = self.players[self.turn_index]
    if bot.is_bot:
        # Just call for now
        return self.handle_player_action("bet", 50)

if __name__ == "__main__":
    app.run(debug=True)