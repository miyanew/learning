import random
from Strategy import Strategy
from Hand import Hand


class ProbStrategy(Strategy):
    def __init__(self, seed):
        self.random = random.Random(seed)
        self.prev_hand_value = 0
        self.current_hand_value = 0
        self.history = [[1, 1, 1], [1, 1, 1], [1, 1, 1]]

    def next_hand(self):
        bet = self.random.randint(0, self._get_sum(self.current_hand_value) - 1)
        if bet < self.history[self.current_hand_value][0]:
            handvalue = 0
        elif (
            bet
            < self.history[self.current_hand_value][0]
            + self.history[self.current_hand_value][1]
        ):
            handvalue = 1
        else:
            handvalue = 2
        self.prev_hand_value = self.current_hand_value
        self.current_hand_value = handvalue
        return Hand.get_hand(handvalue)

    def _get_sum(self, handvalue):
        return sum(self.history[handvalue])

    def study(self, win):
        if win:
            self.history[self.prev_hand_value][self.current_hand_value] += 1
        else:
            self.history[self.prev_hand_value][(self.current_hand_value + 1) % 3] += 1
            self.history[self.prev_hand_value][(self.current_hand_value + 2) % 3] += 1
