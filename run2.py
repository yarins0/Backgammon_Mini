from tkinter import Tk
from GUI import BackgammonGameGUI
from Constants import EVAL_DISTRIBUTION, NETWORK_TRAINING

import random

NUM_AI_PLAYERS = 5  # Adjust the number of AI players
UNIT_RATIO = 0.05  # Ratio unit (0.05 = 1/20)


def generate_random_ratios():
    total_units = int(1.0/UNIT_RATIO)             # Total number of units
    num_factors = len(EVAL_DISTRIBUTION)            # Number of ratios to generate

    # Generate random integers that sum to total_units
    ratios = []
    remaining = total_units
    for _ in range(num_factors - 1):
        # Ensure each ratio is at least 1 (UNIT_RATIO when scaled)
        r = random.randint(0, remaining) # Generate a random integer between 0 (min_value) and remaining (max_value)
        ratios.append(r)
        remaining -= r
    ratios.append(remaining)  # Assign the remaining units to the last ratio

    # Shuffle the ratios to randomize their order
    random.shuffle(ratios)

    return {
        "prime_structure": ratios[0] * UNIT_RATIO,
        "anchors": ratios[1] * UNIT_RATIO,
        "blots": ratios[2] * UNIT_RATIO,
        "race_advantage": ratios[3] * UNIT_RATIO,
        "home_board_strength": ratios[4] * UNIT_RATIO,
        "captured_pieces": ratios[5] * UNIT_RATIO
    }

def print_players_ratios(players):
    i=0
    for player in players:
        if player[0] == "AI":
            print(f"AI player {i} with ratios: {player[1]}")
        i += 1

def turnament():
    window = Tk()
    window.title("Backgammon AI Tournament")

    if NETWORK_TRAINING:
        players = ["AI"] * NUM_AI_PLAYERS  # Generate a list of AI players
    else: # Generate a list of AI players with random ratios
        players = ["AI"]
        for _ in range(NUM_AI_PLAYERS):
            ratios = generate_random_ratios()
            players.append(["AI", ratios])

    # Initialize the game GUI with the list of players
    game_gui = BackgammonGameGUI(window, players)

    # Start the GUI event loop
    window.mainloop()

    print_players_ratios(players)

if __name__ == "__main__":
    turnament()
