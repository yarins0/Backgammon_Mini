from tkinter import Tk
from GUI import BackgammonGameGUI
import random

import random

def generate_random_ratios():
    # Generate random integers that sum to 100
    ratios = []
    remaining = 100
    num_factors = 6  # Number of ratios to generate
    for _ in range(num_factors - 1):
        r = random.randint(1, remaining - (num_factors - len(ratios) - 1))
        ratios.append(r)
        remaining -= r
    ratios.append(remaining)  # Assign the remaining value to the last ratio

    # Shuffle the ratios to randomize their order
    random.shuffle(ratios)

    # Convert ratios to decimal form, ensuring they are multiples of 0.01
    return {
        "prime_structure": ratios[0] / 100,
        "anchors": ratios[1] / 100,
        "blots": ratios[2] / 100,
        "race_advantage": ratios[3] / 100,
        "home_board_strength": ratios[4] / 100,
        "captured_pieces": ratios[5] / 100
    }

if __name__ == "__main__":
    window = Tk()
    window.title("Backgammon AI Tournament")

    # Generate a list of AI players with random ratios
    players = []
    num_ai_players = 50  # Adjust the number of AI players
    for _ in range(num_ai_players):
        ratios = generate_random_ratios()
        players.append(["AI", ratios])

    # Initialize the game GUI with the list of players
    game_gui = BackgammonGameGUI(window, players)

    # Start the GUI event loop
    window.mainloop()

    i=0
    for player in players:
        if player[0] == "AI":
            print(f"AI player {i} with ratios: {player[1]}")
        i += 1
