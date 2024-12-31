from tkinter import Tk
from GUI import BackgammonGameGUI
from Constants import EVAL_DISTRIBUTION

import random

def generate_random_ratios():
    unit_ratio = 0.05
    total_units = int(1.0/unit_ratio)    # Total units (20 * 0.05 = 1.0)
    num_factors = len(EVAL_DISTRIBUTION)            # Number of ratios to generate

    # Generate random integers that sum to total_units
    ratios = []
    remaining = total_units
    for _ in range(num_factors - 1):
        # Ensure each ratio is at least 1 (0.05 when scaled)
        min_value = 1
        max_value = remaining - (num_factors - len(ratios) - 1) * min_value
        r = random.randint(min_value, max_value)
        ratios.append(r)
        remaining -= r
    ratios.append(remaining)  # Assign the remaining units to the last ratio

    # Shuffle the ratios to randomize their order
    random.shuffle(ratios)

    return {
        "prime_structure": ratios[0] * unit_ratio,
        "anchors": ratios[1] * unit_ratio,
        "blots": ratios[2] * unit_ratio,
        "race_advantage": ratios[3] * unit_ratio,
        "home_board_strength": ratios[4] * unit_ratio,
        "captured_pieces": ratios[5] * unit_ratio
    }

if __name__ == "__main__":
    window = Tk()
    window.title("Backgammon AI Tournament")

    # Generate a list of AI players with random ratios
    players = []
    num_ai_players = 30  # Adjust the number of AI players
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
