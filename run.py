import sys
import msvcrt
from tkinter import Tk
from BackgammonGameManager import BackgammonGameManager
from TournamentSetup import TournamentSetupWindow, TournamentResultsScreen
from Constants import *


class GameLooper:
    def __init__(self):
        self.game_count = 0
        self.current_game = None
        self.players = []  # Set by the tournament setup screen before first game
        self.start_board = START_BOARD
        self.game_in_progress = False

    def check_for_quit(self, window):
        """Checks for 'q' key press to quit the application."""
        if msvcrt.kbhit():
            if msvcrt.getch().lower() == b'q':
                print("User requested to quit. Stopping.")
                window.destroy()
                sys.exit(0)
        window.after(200, lambda: self.check_for_quit(window))

    def launch_tournament(self, window, on_complete=None):
        """Destroys any existing game widgets and starts a new tournament."""
        print(f"Starting tournament #{self.game_count + 1}")

        if self.current_game is not None:
            for widget in window.winfo_children():
                widget.destroy()

        self.game_count += 1

        def _on_done(players, scores, winner_idx):
            self.game_in_progress = False
            if ONE_RUN:
                print("Game completed. ONE_RUN is set to True. Exiting.")
                return
            if on_complete:
                on_complete(players, scores, winner_idx)

        self.current_game = BackgammonGameManager(
            window, self.players, self.start_board, on_complete=_on_done
        )
        self.game_in_progress = True

def main():
    window = Tk()
    manager = GameLooper()
    manager.check_for_quit(window)

    # current_screen holds a ref to whichever screen is active so it can be
    # destroyed before the next one is built
    current_screen = [None]

    def show_setup():
        current_screen[0] = TournamentSetupWindow(window, on_tournament_start)

    def on_tournament_start(players):
        current_screen[0].destroy()
        manager.players = players
        manager.launch_tournament(window, on_tournament_complete)

    def on_tournament_complete(players, scores, winner_idx):
        for widget in window.winfo_children():
            widget.destroy()
        current_screen[0] = TournamentResultsScreen(
            window, players, scores, winner_idx, show_setup
        )

    show_setup()
    window.mainloop()

if __name__ == "__main__":
    main()