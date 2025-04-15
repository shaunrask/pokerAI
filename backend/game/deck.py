import random

SUITS = ["h", "d", "c", "s"]
RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]


class Deck:
    def __init__(self):
        self.cards = [Card(suit,rank) for suit in SUITS for rank in RANKS]
        random.shuffle(self.cards)

    def deal(self,n):
        return [self.cards.pop() for _ in range(n)]

class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __str__(self):
        return f"{self.rank}{self.suit}"

    def __repr__(self):
        return f"{self.rank}{self.suit}"

    def __eq__(self, other):
        return self.suit == other.suit and self.rank == other.rank

