from tkinter import Tk
from GUI import *  # Ensure this import matches your file structure
import random

def generate_random_ratios():
    # Generate random ratios that sum to 1
    ratios = [random.random() for _ in range(5)]
    total = sum(ratios)
    return {
        "prime_structure": ratios[0] / total,
        "anchors": ratios[1] / total,
        "blots": ratios[2] / total,
        "race_advantage": ratios[3] / total,
        "home_board_strength": ratios[4] / total
    }

# Create a list of players with different AI configurations
players = []

# Generate 10 different AI configurations
for _ in range(10):
    ratios = generate_random_ratios()
    players.append(["AI", ratios])

# Initialize the Tkinter window
window = Tk()
window.title("Backgammon Game")

# Create an instance of the BackgammonGameGUI with the players array
game = BackgammonGameGUI(window, players)

# Start the Tkinter main loop
window.mainloop()