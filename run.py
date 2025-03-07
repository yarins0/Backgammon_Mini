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
    "neural_vs_mcts": [NEURAL_AI, [MCTS_AI, ratios1, 2.2]],
    "neural_vs_neural": [NEURAL_AI, NEURAL_AI],
    "human_vs_neural": [NEURAL_AI, HUMAN],
    "human_vs_random": [HUMAN, RAND_AI],
    "human_vs_human": [HUMAN, HUMAN],
    "neural_vs_random": [NEURAL_AI, RAND_AI],
    "mcts_vs_random": [MCTS_AI, RAND_AI],
    "min_max_vs_neural": [MIN_MAX_AI, NEURAL_AI],
    "min_max_vs_human": [MIN_MAX_AI, HUMAN],
    "min_max_vs_mcts": [MIN_MAX_AI, MCTS_AI],
    "random_vs_random": [RAND_AI, RAND_AI],
    "min_max_vs_min_max": [MIN_MAX_AI, [MIN_MAX_AI, ratios1, 2]],
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
        self.players = PLAYER_CONFIGURATIONS["human_vs_human"]  # Default configuration
        self.start_board = START_BOARD  # Default board configuration
        #self.start_board = [0, 0, 0, -4, 0, -4, 0, 0, 0, -1, -1, 4, 1, 0, 1, 0, 2, 2, 5, -1, 0, -2, -1, 0, 0, 1, 0, 0]
        self.game_in_progress = False

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
        self.current_game = BackgammonGameManager(window, self.players, self.start_board)
        self.game_in_progress = True
        return self.current_game.winner_player is not None  # Return True if the game is finished immediately
    
    def check_game_status(self, window):
        """Checks if the current game has finished and schedules the next game if needed."""
        if self.current_game and self.current_game.winner_player is not None:
            # Game has finished
            self.game_in_progress = False
            
            if ONE_RUN:
                print("Game completed. ONE_RUN is set to True. Exiting.")
                return
            
            # Schedule next game after a delay
            window.after(100, lambda: self.schedule_next_game(window))
        else:
            # Game still in progress, check again after a delay
            window.after(200, lambda: self.check_game_status(window))
    
    def schedule_next_game(self, window):
        """Schedules the next game with proper cleanup."""
        if not self.game_in_progress:
            if self.launch_new_game(window):
                # If the game finished immediately (unlikely), handle it
                self.game_in_progress = False
                window.after(1000, lambda: self.schedule_next_game(window))
            else:
                # Start monitoring the new game
                self.check_game_status(window)

def main():
    window = Tk()
    manager = GameLooper()
    manager.check_for_quit(window)
    manager.schedule_next_game(window)
    
    window.mainloop()

if __name__ == "__main__":
    main()