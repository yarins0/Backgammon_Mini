import sys
import msvcrt
from tkinter import Tk
from GUI import BackgammonGameGUI  # Adjust import to match your file structure
from Constants import ONE_RUN, AI, HUMAN, MIN_MAX_AI, MCTS_AI
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

# A few possible player configuration examples
players_human_vs_human = ["Human", "Human"]
players_human_vs_ai = ["Human", "AI"]
players_ai_vs_human = ["AI", "Human"]
players_ai_vs_ai = ["AI", "AI"]
players_ai_vs_ai_net = ["AI", ["AI",ratios1,"HeuristicNet_copy1.pth"]]


# Multiple AIs with different ratio settings
players_different_ratios = [
    ["AI", ratios1],
    ["AI", ratios2],
    ["AI", ratios3],
    ["AI", ratios4],
    ["AI", ratios5]
]

game_count = 0

# Define player settings here, e.g. AI vs AI
players_to_use = players_ai_vs_ai

def check_for_quit(window):
    """
    Periodically checks if the user pressed 'q'. If so, stop the program.
    Otherwise, schedule another check in 200 milliseconds.
    """
    if msvcrt.kbhit():
        key_pressed = msvcrt.getch()
        if key_pressed.lower() == b'q':
            print("User requested to quit. Stopping.")
            window.destroy()
            sys.exit(0)
    window.after(200, check_for_quit, window)

def launch_new_game(window, players):
    """
    Create a fresh BackgammonGameGUI instance. No game methods are called.
    """
    global game_count
    print(f"Current game count: {game_count}")
    game_count += 1  # Increment the count each time a new game is launched
    BackgammonGameGUI(window, players)

def loop_games(window, players):
    """
    Continuously launch new games without calling any methods on the game object.
    In this example, each new instance is created about every 3 seconds.
    """
    launch_new_game(window, players)

    if ONE_RUN:
        # Do not schedule another game if only one game should be played
        print("ONE_GAME flag is True; only one game will be played.")
        return
    
    # Schedule the next launch
    window.after(100, loop_games, window, players)

def main():
    window = Tk()
    window.title("Backgammon Game")

    # Start a continuous loop of new games
    loop_games(window, players_to_use)

    # Start checking for 'q' presses to quit
    check_for_quit(window)

    # Block until the user quits
    window.mainloop()

if __name__ == "__main__":
    main()