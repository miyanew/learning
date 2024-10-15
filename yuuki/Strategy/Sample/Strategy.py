from abc import ABC, abstractmethod


class Strategy(ABC):
    @abstractmethod
    def next_hand(self):
        pass

    @abstractmethod
    def study(self, win):
        pass
