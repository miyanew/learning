import random
from Hand import Hand
from Strategy import Strategy


class WinningStrategy(Strategy):
    def __init__(self, seed):
        self.random = random.Random(seed)
        self.won = False
        self.prev_hand = None

    def next_hand(self):
        if not self.won:
            self.prev_hand = Hand.get_hand(self.random.randint(0, 2))
        return self.prev_hand

    def study(self, win):
        self.won = win
