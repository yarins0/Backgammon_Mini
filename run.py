from tkinter import Tk
from GUI import *  # Ensure this import matches your file structure

ratios1 = {
    "prime_structure": 0.1,
    "anchors": 0.1,
    "blots": 0.2,
    "race_advantage": 0.3,
    "home_board_strength": 0.1,
    "captured_pieces": 0.2
}

ratios2 = {
    "prime_structure": 0.1,
    "anchors": 0.2,
    "blots": 0.1,
    "race_advantage": 0.2,
    "home_board_strength": 0.2,
    "captured_pieces": 0.2
}

# This file is the entry point for the program. It creates the Tkinter window and the BackgammonGame instance.
players1 = ["Human", "Human"]
players2 = ["Human", "AI"]
players3 = ["AI", "Human"]
players4 = ["AI", "AI", "AI", "AI"]
players5 = [["AI",ratios1], "AI"]
players6 = [["AI",ratios1], ["AI",ratios2]]
# Initialize the Tkinter window
window = Tk()
window.title("Backgammon Game")

# Create an instance of the BackgammonGame

game = BackgammonGameGUI(window, players5)

# Start the Tkinter main loop
window.mainloop()