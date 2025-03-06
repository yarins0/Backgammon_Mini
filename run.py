import sys
import msvcrt
from tkinter import Tk
from BackgammonGameManager import BackgammonGameManager  # Adjust import to match your file structure
from Constants import *

# Example ratio dictionaries
ratios1 = {
    "prime_structure": 1,
    "anchors": 0,
    "blots": 0,
    "race_advantage": 0,
    "home_board_strength": 0,
    "captured_pieces": 0
}

ratios2 = {
    "prime_structure": 0.5,
    "anchors": 0.05,
    "blots": 0.45,
    "race_advantage": 0.0,
    "home_board_strength": 0.0,
    "captured_pieces": 0.0
}

ratios3 = {
    "prime_structure": 0.0,
    "anchors": 0.0,
    "blots": 0.05,
    "race_advantage": 0.2,
    "home_board_strength": 0.0,
    "captured_pieces": 0.75
}

ratios4 = {
    "prime_structure": 0.33,
    "anchors": 0.0,
    "blots": 0.33,
    "race_advantage": 0.0,
    "home_board_strength": 0.0,
    "captured_pieces": 0.34
}

ratios5 = {
    "prime_structure": 0.9,
    "anchors": 0.0,
    "blots": 0.1,
    "race_advantage": 0.0,
    "home_board_strength": 0.0,
    "captured_pieces": 0.0
}


# Player Configurations
PLAYER_CONFIGURATIONS = {
    "human_vs_human": ["Human", "Human"],
    "human_vs_ai": ["Human", "AI"],
    "ai_vs_human": ["AI", "Human"],
    "neural_vs_neural": [NEURAL_AI, NEURAL_AI],
    "ai_vs_neural": [HEUR_AI, NEURAL_AI, NEURAL_AI, HEUR_AI],
}

# Multiple AIs with different ratio settings
players_different_ratios = [
    ["AI", ratios1],
    ["AI", ratios2],
    ["AI", ratios3],
    ["AI", ratios4],
    ["AI", ratios5]
]

class GameLooper:
    def __init__(self):
        self.game_count = 0
        self.current_game = None
        self.players = PLAYER_CONFIGURATIONS["ai_vs_neural"]  # Default configuration
        #self.start_board = [0, 0, 0,-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 3, 1, 0, 2, 0, 0, 5, 14]

    def check_for_quit(self, window):
        """Checks for 'q' key press to quit the application."""
        if msvcrt.kbhit():
            if msvcrt.getch().lower() == b'q':
                print("User requested to quit. Stopping.")
                window.destroy()
                sys.exit(0)
        window.after(200, lambda: self.check_for_quit(window))

    def launch_new_game(self, window):
        """Creates a new game instance after cleaning up the previous one."""
        print(f"Starting game #{self.game_count + 1}")
        
        # Clean up previous game
        if self.current_game is not None:
            for widget in window.winfo_children():
                widget.destroy()
        
        # Create new game
        self.game_count += 1
        self.current_game = BackgammonGameManager(window, self.players)
        return self.current_game.winner_player != None # Return True if the game is finished
    
    def schedule_next_game(self, window):
        """Schedules the next game with proper cleanup."""
        if ONE_RUN and self.game_count > 0:
            print("ONE_RUN is set to True. Exiting.")
            return
        if self.launch_new_game(window):
            self.schedule_next_game(window)
        window.after(200, lambda: self.schedule_next_game(window))

def main():
    window = Tk()
    manager = GameLooper()
    manager.check_for_quit(window)
    manager.schedule_next_game(window)
    
    window.mainloop()

if __name__ == "__main__":
    main()