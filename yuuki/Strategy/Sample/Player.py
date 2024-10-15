class Player:
    def __init__(self, name, strategy):
        self.name = name
        self.strategy = strategy
        self.wincount = 0
        self.losecount = 0
        self.gamecount = 0

    def next_hand(self):
        return self.strategy.next_hand()

    def win(self):
        self.strategy.study(True)
        self.wincount += 1
        self.gamecount += 1

    def lose(self):
        self.strategy.study(False)
        self.losecount += 1
        self.gamecount += 1

    def even(self):
        self.gamecount += 1

    def __str__(self):
        return f"[{self.name}: {self.gamecount} games, {self.wincount} win, {self.losecount} lose]"
