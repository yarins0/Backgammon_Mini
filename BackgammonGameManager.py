from Players.Heuristic_Player import Heuristic_Player
from Players.MCTS_Player import MCTS_Player
from Players.Min_Max_Player import Min_Max_Player
from Players.Neural_Player import Neural_Player
from Players.Human_Player import Human_Player
from Players.Random_Player import Random_Player
from HeuristicNet import boards_based_training
from GUI import BackgammonGameGUI
from Constants import *
import random

class BackgammonGameManager:
    def __init__(self, window, players, board= START_BOARD):
        self.window = window
        self.players = players
        self.scores = [0] * len(self.players)
        self.current_game_index = 0  # Track the current game index
        self.winner_player = None
        self.winner_idx = None

        # Initialize the game board
        self.board = self.start_board = board.copy()
        
        # Initialize the first pair of players
        self.initialize_players(0, 1)

        # Initialize the UI components
        self.gui = BackgammonGameGUI(self.window, self)

        # Start the first game
        self.start_next_game()


    def initialize_players(self, i, j):
        # Create player instances with the shared board
        self.black = self.parse_player(self.players[i], BLACK)
        self.white = self.parse_player(self.players[j], WHITE)

    def parse_player(self, player, color):
        """
        Parse the player input to determine the type and ratios.
        """
        if player == HUMAN:
            return Human_Player(color, board=self.start_board) # Human player
        elif player == RAND_AI:
            return Random_Player(color, board=self.start_board)  # Random AI player
        elif player == HEUR_AI:
            return Heuristic_Player(color, board=self.start_board)
        elif player == MIN_MAX_AI:
            return Min_Max_Player(color, board=self.start_board)
        elif player == MCTS_AI:
            return MCTS_Player(color, board=self.start_board)
        elif player == NEURAL_AI:
            return Neural_Player(color, board=self.start_board)
        elif isinstance(player, list):
            if player[0] == HEUR_AI:
                return Heuristic_Player(color, board=self.start_board, ratios=player[1])
            elif player[0] == NEURAL_AI:
                return Neural_Player(color, board=self.start_board, model_path=player[1])
            elif player[0] == MCTS_AI:
                return MCTS_Player(color, board=self.start_board, ratios=player[1], c=player[2])
            elif player[0] == MIN_MAX_AI:
                return Min_Max_Player(color, board=self.start_board, ratios=player[1], depth=player[2])
            else:
                raise ValueError("Invalid player input format")
        else:
            raise ValueError("Invalid player input format")

    def start_next_game(self):
        if self.current_game_index < len(self.players) * (len(self.players) - 1) // 2:
            # Initialize the game board
            self.board = self.start_board.copy()

            self.black_idx, self.white_idx = self.get_player_indices(self.current_game_index)
            self.current_game_index += 1

            self.initialize_players(self.black_idx, self.white_idx)
            self.start_game()
        else:
            # All games are completed
            print("All games completed.")
            print("Scores:", self.scores)
            self.winner_idx = self.scores.index(max(self.scores))
            self.winner_player = self.players[self.winner_idx]

            print(f"Overall winner: Player {self.winner_idx} with {self.scores[self.winner_idx]} wins")
            self.gui.set_title(f"Overall winner: Player {self.winner_idx + 1} with {self.scores[self.winner_idx]} wins")
         
    def start_game(self):
        # Reset the board history and clear the board
        self.reset_board_history()
        self.gui.clear_board()

        # Start the first turn with white
        self.turn = WHITE

        self.update_and_render_board()

        # Print starting game information
        print(f"Starting game between {self.white} and {self.black}")
        self.gui.set_title(f"Starting game between {self.white} and {self.black}")

        self.prepare_turn()

    def get_player_indices(self, game_index):
        # Calculate player indices for the current game using round-robin scheduling
        num_players = len(self.players)
        i = game_index % num_players
        j = (game_index + i) % num_players
        if i == j:
            j = (j + 1) % num_players
        return i, j

    def roll(self):
        """Handles the dice roll for a human player and starts the turn timer."""
        self.rolls = roll()
        
        if DEBUG_MODE:
            print(f"{self.current_player()} rolled: {self.rolls}")
        
        # Disable the roll button until the turn ends
        self.gui.disable_roll_button(True)
        self.gui.set_rolls(self.rolls)
        self.gui.set_title("Choose a piece to move")

        # Start (or restart) the timer
        self.gui.start_timer()

        return self.rolls


    def AI_turn(self):
        computer_roll = self.roll()
        current_player = self.current_player()

        #try:
        move_sequence = current_player.choose_move(self.board , computer_roll)
        if move_sequence:
            for move in move_sequence:
                # Execute each move
                from_pos, to_pos = move
                for roll in computer_roll:
                    try:
                        if current_player.move_piece(from_pos, to_pos, roll, simulate = True) == roll:
                            break
                    except ValueError as e:
                        pass
                self.update_and_render_board()
                self.window.after(AI_DELAY)  # Optional: pause for AI_DELAY ms between moves
                
        self.end_turn()

    def human_move1(self, event):
        if self.current_board_index != len(self.board_history) - 1:
            self.gui.set_title("You can only make moves on the latest board state.")
            return

        self.gui.select(event)

        if not self.current_player().is_piece_at_position(self.gui.selected, self.board, self.turn):
            self.gui.set_title("That's an invalid piece to pick")
            return
        self.gui.set_title('Choose a position to move it to (right click)')

    def human_move2(self, event):
        if self.current_board_index != len(self.board_history) - 1:
            self.gui.set_title("You can only make moves on the latest board state.")
            return

        if not self.rolls:
            self.gui.set_title("No dice rolls available to make a move.")
            return
        
        self.gui.goto(event)

        for roll in self.rolls:
            try:
                used_die_value = self.current_player().move_piece(self.gui.selected, self.gui.destination, roll)
                if used_die_value == roll:
                    # Remove the used die value from the available rolls
                    self.rolls.remove(used_die_value)
                    self.gui.set_rolls(self.rolls)

                    # Update the board after the move
                    self.board = self.current_player().board
                    self.update_and_render_board()
                    self.check_win_condition()
                    break
            except ValueError as e:
                self.gui.set_title(str(e))


        if not self.rolls:
            self.gui.reset_movement()
            self.end_turn()


    def current_player(self):
        return self.white if self.turn == WHITE else self.black

    def other_player(self):
        return self.black if self.turn == WHITE else self.white
       
    def prepare_turn(self):
        current_player = self.current_player()
        if DEBUG_MODE:
            print(f"{self.board}")
            print(f"{current_player} turn started")
                
        if current_player.is_human:
            self.gui.set_title(f"It's the {current_player} player's turn! Roll the dice!")
            self.gui.disable_roll_end_buttons(False)
        else:
            self.gui.disable_roll_end_buttons(True)
            self.AI_turn()

    def end_turn(self):
        """Ends the current turn, re-enables the roll button, and resets UI."""
        self.gui.set_rolls()
        self.gui.set_time_remaining()

        # Stop the timer to avoid confusion on next turn
        self.gui.timer_running = False

        if self.check_win_condition():
            return # Do not proceed if the game is over

        self.switch_turn()
        self.prepare_turn()

    def switch_turn(self):
        self.turn = WHITE if self.turn == BLACK else BLACK

    def check_win_condition(self):
        current_player = self.current_player()
        if current_player.win():
            print(f'{current_player} has won the game!')
            self.gui.set_title(f'{current_player} has won the game!')

            # Update scores
            idx = self.white_idx if self.turn == WHITE else self.black_idx
            self.scores[idx] += 1

            self.gui.disable_buttons()

            if (NETWORK_TRAINING):
                boards_based_training(self.board_history)

            # Schedule the next game after a delay or end the session
            #self.start_next_game()
            self.window.after(AI_DELAY, self.start_next_game)

            return True
        return False
    
    def is_over(self):
        return self.white.win() or self.black.win()

    def update_and_render_board(self):
        # Update the board state and render it immediately
        self.board_history.append([self.board.copy(), self.turn])
        self.current_board_index += 1
        self.gui.render_board(self.board)
    
    def show_previous_board(self):
        if self.current_board_index > 0:
            self.current_board_index -= 1
            previous_board = self.board_history[self.current_board_index][0]
            self.gui.render_board(previous_board)
        else:
            print("No previous board state available.")
            self.gui.set_title("No previous board state available.")

    def show_next_board(self):
        if self.current_board_index < len(self.board_history) - 1:
            self.current_board_index += 1
            next_board = self.board_history[self.current_board_index][0]
            self.gui.render_board(next_board)
        else:
            print("No next board state available.")
            self.gui.set_title("No next board state available.")
    def reset_board_history(self):
        self.board_history = []
        self.current_board_index = -1
def roll():
    r = [random.randint(1,6), random.randint(1,6)]
    if r[0] == r[1]:
        r = [r[0], r[0], r[0], r[0]]
    return r

def generate_board(white_pieces , black_pieces):
        board = [0] * 28
        for point in white_pieces:
            if point == 0: # white captured
                board[26] += 1
            elif point == 25:
                board[24] += 1 # white out
            else:
                board[point - 1] += 1

        for point in black_pieces:
            if point == 25:  # black captured
                board[27] += 1
            elif point == 0:
                board[25] += 1  # black out
            else:
                board[point - 1] -= 1


        return board


