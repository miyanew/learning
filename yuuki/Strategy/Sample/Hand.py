# from enum import Enum


# class Hand(Enum):
class Hand():
    # ROCK = (0, "グー")
    # SCISSORS = (1, "チョキ")
    # PAPER = (2, "パー")

    def __init__(self, handvalue):
        self.handvalue = handvalue
        # self.name = self.hands[handvalue][1]

    @classmethod
    def get_hand(cls, handvalue):
        # return self.hands[handvalue]
        # return [hand for hand in cls if hand.handvalue == handvalue][0]
        return cls(handvalue)

    def is_stronger_than(self, hand):
        return self._fight(hand) == 1

    def is_weaker_than(self, hand):
        return self._fight(hand) == -1

    def _fight(self, hand):
        if self == hand:
            return 0
        elif (self.handvalue + 1) % 3 == hand.handvalue:
            return 1
        else:
            return -1

    def __str__(self):
        # return self.name
        return ["グー", "チョキ", "パー"][self.handvalue]
