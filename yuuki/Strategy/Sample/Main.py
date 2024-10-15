from Player import Player
from WinningStrategy import WinningStrategy
from ProbStrategy import ProbStrategy


def main():
    seed1 = 314
    seed2 = 15
    player1 = Player("Taro", WinningStrategy(seed1))
    player2 = Player("Hana", ProbStrategy(seed2))

    for _ in range(10000):
        next_hand1 = player1.next_hand()
        next_hand2 = player2.next_hand()
        if next_hand1.is_stronger_than(next_hand2):
            print(f"Winner: {player1}")
            player1.win()
            player2.lose()
        elif next_hand2.is_stronger_than(next_hand1):
            print(f"Winner: {player2}")
            player1.lose()
            player2.win()
        else:
            print("Even...")
            player1.even()
            player2.even()

    print("Total result:")
    print(player1)
    print(player2)


if __name__ == "__main__":
    main()
