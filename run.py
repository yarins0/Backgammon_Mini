from tkinter import Tk
from GUI import *  # Ensure this import matches your file structure

ratios1 = {
    "prime_structure": 1,
    "anchors": 0,
    "blots": 0,
    "race_advantage": 0,
    "home_board_strength": 0,
    "captured_pieces": 0
}

ratios2 = {'prime_structure': 0.5, 'anchors': 0.05, 'blots': 0.45, 'race_advantage': 0.0, 'home_board_strength': 0.0, 'captured_pieces': 0.0}
ratios3 = {'prime_structure': 0.0, 'anchors': 0.0, 'blots': 0.05, 'race_advantage': 0.2, 'home_board_strength': 0.0, 'captured_pieces': 0.75}
ratios4 = {'prime_structure': 0.33, 'anchors': 0.0, 'blots': 0.33, 'race_advantage': 0.0, 'home_board_strength': 0.0, 'captured_pieces': 0.34}
ratios5 = {'prime_structure': 0.9, 'anchors': 0.0, 'blots': 0.1, 'race_advantage': 0.0, 'home_board_strength': 0.0, 'captured_pieces': 0.0}

# This file is the entry point for the program. It creates the Tkinter window and the BackgammonGame instance.
players1 = ["Human", "Human"]
players2 = ["Human", "AI"]
players3 = ["AI", "Human"]
players4 = ["AI", "AI"]
players5 = [["AI",ratios1], ["AI",ratios5]]
players6 = [["AI",ratios1], ["AI",ratios2], ["AI",ratios3], ["AI",ratios4], ["AI",ratios5]]
# Initialize the Tkinter window
window = Tk()
window.title("Backgammon Game")

# Create an instance of the BackgammonGame

game = BackgammonGameGUI(window, players5)

# Start the Tkinter main loop
window.mainloop()