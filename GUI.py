from tkinter import *
from Player import *
from AI_Player import AI_Player
from Human_Player import Human_Player
from game_logic import roll
from HeuristicNet import boards_based_training
from Constants import *
import random

TRI_WIDTH = 50
TRI_HEIGHT = 200

class BackgammonGameGUI:
    def __init__(self, window, players, board= START_BOARD):
        self.window = window
        self.players = players
        self.scores = [0] * len(self.players)
        self.auto_render = True  # Flag to control automatic rendering
        self.current_game_index = 0  # Track the current game index

        # Initialize the game board
        self.board = self.start_board = board.copy()
        
        # Initialize the first pair of players
        self.initialize_players(0, 1)

        # Initialize the UI components
        self.create_board()

        # Start the first game
        self.start_next_game()



    def initialize_players(self, i, j):
        black_player, black_ratios, black_path = self.parse_player(self.players[i], BLACK)
        white_player, white_ratios, white_path = self.parse_player(self.players[j], WHITE)

        # Create player instances with the shared board
        self.black = AI_Player(BLACK, self.board, black_ratios, black_path) if black_player == AI else Human_Player(BLACK, self.board)
        self.white = AI_Player(WHITE, self.board, white_ratios, white_path) if white_player == AI else Human_Player(WHITE, self.board)

    def parse_player(self, player, color):
        """
        Parse the player input to determine the type and ratios.
        """
        if isinstance(player, list) and len(player) == 2 and player[0] == AI:
            return AI, player[1] , PATH  # AI with specified ratios and default path
        elif isinstance(player, list) and len(player) == 3 and player[0] == AI:
            return AI, player[1] ,player[2]  # AI with specified ratios and path
        elif player == AI:
            return AI, EVAL_DISTRIBUTION, PATH  # AI with default ratios AND PATH
        elif player == HUMAN:
            return HUMAN, None, None  # Human player
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
            winner_idx = self.scores.index(max(self.scores))
            winner_player = self.players[winner_idx]

            print(f"Overall winner: Player {winner_idx} with {self.scores[winner_idx]} wins")
            self.title.set(f"Overall winner: Player {winner_idx + 1} with {self.scores[winner_idx]} wins")

            
    def start_game(self):
        self.clear_board()
        self.update_and_render_board()

        # Print starting game information
        print(f"Starting game between {self.white} and {self.black}")
        self.title.set(f"Starting game between {self.white} and {self.black}")

        # Start the first turn with white
        self.turn = WHITE
        self.prepare_turn()

    def get_player_indices(self, game_index):
        # Calculate player indices for the current game
        num_players = len(self.players)
        i = game_index // (num_players - 1)
        j = game_index % (num_players - 1)
        if j >= i:
            j += 1
        return i, j

    def clear_board(self):
        # Clear the canvas content if it exists
        if hasattr(self, '_canvas'):
            self._canvas.delete('all')
            self.draw_triangles()  # Redraw the triangles after clearing
        else:
            print("Canvas not initialized yet.")

        # Reset board history
        self.board_history = []
        self.current_board_index = -1

        # Reset the UI components
        self.rolls.set('')
        self.title.set("It's a new game! Roll the dice to start!")
        self.time_remaining.set('')

    def create_board(self):
        # Initialize turn if not already set
        if not hasattr(self, 'turn'):
            self.turn = WHITE

        # Create the top frame first
        self.top_frame = Frame(self.window)
        self.top_frame.pack(pady=5)

        self.title = StringVar(value=f"It's {self.turn}'s turn! Roll the dice!")
        self.time_remaining = StringVar()

        # Create the labels
        self.turnInst = Label(self.top_frame, textvariable=self.title)
        self.timer_label = Label(self.top_frame, textvariable=self.time_remaining)

        # Pack the labels into self.top_frame
        self.turnInst.pack()
        self.timer_label.pack()

        # Create the canvas and other widgets
        self._canvas = Canvas(self.window, width=13 * TRI_WIDTH, height=3 * TRI_HEIGHT)
        self.rolls = StringVar()
        self.roll_frame = Frame(self.window)

        self.time_left = TURN_TIME

        self.rollButton = Button(self.roll_frame, text='Roll', command=self.roll)
        self.dieLabel = Label(self.roll_frame, textvariable=self.rolls, font=("Helvetica", 16))
        self.endButton = Button(self.roll_frame, text='End Turn (if stuck)', command=self.end_turn)

        # Add buttons to navigate board history
        self.prevBoardButton = Button(self.roll_frame, text='<<', command=self.show_previous_board)
        self.nextBoardButton = Button(self.roll_frame, text='>>', command=self.show_next_board)

        self.setup_board_ui()
        self.render()

    def draw_triangles(self):
        # Draw the upper row of triangles
        for space in range(12):
            color = '#C19A6B' if space % 2 != 0 else 'white'  # Alternate colors
            self._canvas.create_polygon(
                space * TRI_WIDTH, 0,
                (space + 1) * TRI_WIDTH, 0,
                (space + 0.5) * TRI_WIDTH, TRI_HEIGHT,
                fill=color,
                outline='black'  # Add black frame
            )
        # Draw the lower row of triangles
        for space in range(12):
            color = 'white' if space % 2 != 0 else '#C19A6B'  # Alternate colors
            self._canvas.create_polygon(
                space * TRI_WIDTH, int(3 * TRI_HEIGHT),
                (space + 1) * TRI_WIDTH, int(3 * TRI_HEIGHT),
                (space + 0.5) * TRI_WIDTH, int(2 * TRI_HEIGHT),
                fill=color,
                outline='black'  # Add black frame
            )

    def setup_board_ui(self):
        # Draw the triangles on the canvas
        self.draw_triangles()

        # Create and pack the button frame
        self.button_frame = Frame(self.window)
        self.button_frame.pack(pady=5)

        # Pack buttons into the roll_frame
        self.rollButton.pack(side=LEFT, padx=5)
        self.endButton.pack(side=LEFT, padx=5)
        self.prevBoardButton.pack(side=LEFT, padx=5)
        self.nextBoardButton.pack(side=LEFT, padx=5)
        self.dieLabel.pack(side=LEFT, padx=5)

        # Pack the roll_frame into the button_frame
        self.roll_frame.pack()

        # Pack the button_frame into the window
        self.button_frame.pack()

        # Now pack the canvas
        self._canvas.pack(pady=10)

        # Bindings for human move events
        self._canvas.bind('<Button-1>', self.human_move1)
        self._canvas.bind('<Button-3>', self.human_move2)

    def roll(self):
        """Handles the dice roll for a human player and starts the turn timer."""
        self.r = roll()
        self.r.sort()
        rolled = ' '.join(map(str, self.r))
        self.rolls.set(rolled)

        # Disable the roll button until the turn ends
        self.rollButton.config(state=DISABLED)
        self.title.set("Choose a piece to move")

        # Start (or restart) the timer
        self.start_timer()

    def start_timer(self):
        """Starts/restarts the countdown for the human player's turn."""
        # Start the timer
        self.timer_running = True
        self.time_left = TURN_TIME
        self.update_timer()

    def update_timer(self):
        """Updates the countdown label every second until time runs out."""
        if self.time_left > 0:
            self.time_remaining.set(f"Time left: {self.time_left} seconds")
            self.time_left -= 1
            # Schedule the next update in 1 second
            if self.timer_running:
                self.window.after(1000, self.update_timer)
        else:
            # Time’s up, end this turn automatically
            self.title.set("Time's up! Ending your turn.")
            self.end_turn()

    def render(self):
        if self.auto_render:
            # Render the board state
            self.render_board(self.board)
        self._canvas.after(50, self.render)  # Schedule the next render

    def render_board(self, board):
        self._canvas.delete('piece')  # Clear the existing pieces
        # Render pieces based on the board state
        for position, count in enumerate(board):
            if count != 0:
                color = 'white' if (count > 0 and position <= 23) or (position >= 24 and position % 2 == 0) else 'black'
                count = abs(count)
                for pos in range(count):
                    if position < 12:
                        # Top row positions 11 to 0
                        self._canvas.create_oval(
                            (11 - position) * TRI_WIDTH, pos * TRI_WIDTH,
                            (12 - position) * TRI_WIDTH, (pos + 1) * TRI_WIDTH,
                            fill=color, tags='piece'
                        )
                    elif position < 24:
                        # Bottom row positions 12 to 23
                        self._canvas.create_oval(
                            (position - 12) * TRI_WIDTH, int(self._canvas.cget('height')) - ((pos + 1) * TRI_WIDTH),
                            (position - 11) * TRI_WIDTH, int(self._canvas.cget('height')) - (pos * TRI_WIDTH),
                            fill=color, tags='piece'
                        )
                    elif position == 24:  # White captured pieces at top right corner
                        # Adjust coordinates for top right corner
                        self._canvas.create_oval(
                            12 * TRI_WIDTH, (pos) * TRI_WIDTH,
                            13 * TRI_WIDTH, (pos + 1) * TRI_WIDTH,
                            fill='white', tags='piece'
                        )
                    elif position == 25:  # Black captured pieces at bottom right corner
                        # Adjust coordinates for bottom right corner
                        self._canvas.create_oval(
                            12 * TRI_WIDTH, int(self._canvas.cget('height')) - ((pos + 1) * TRI_WIDTH),
                            13 * TRI_WIDTH, int(self._canvas.cget('height')) - (pos * TRI_WIDTH),
                            fill='black', tags='piece'
                        )
                    # Handle borne-off pieces if needed
        self._canvas.update_idletasks()  # Ensure the canvas is refreshed

    def AI_turn(self):
        computer_roll = roll()
        if DEBUG_MODE:
            print(f"Computer roll: {computer_roll}")

        current_player = self.current_player()

        # Convert the dice roll to strings before joining
        rolled = ' '.join(map(str, computer_roll))
        self.rolls.set(rolled)
        self.title.set(f"{current_player} rolled: {rolled}")

        #try:
        move_sequence = current_player.choose_move(self.board , computer_roll)
        if move_sequence:
            for move in move_sequence:
                # Execute each move
                from_pos, to_pos = move
                current_player.move_piece(from_pos, to_pos, computer_roll)
                self.update_and_render_board()
                self.window.after(AI_DELAY)  # Optional: pause for AI_DELAY ms between moves
                
        self.end_turn()

    def human_move1(self, event):
        if self.current_board_index != len(self.board_history) - 1:
            self.title.set("You can only make moves on the latest board state.")
            return

        self.select(event)
        position = self.selected
        current_player = self.current_player()

        if not current_player.is_piece_at_position(position, self.board, current_player.color):
            self.title.set("That's an invalid piece to pick")
            return
        self.title.set('Choose a position to move it to (right click)')

    def human_move2(self, event):
        if self.current_board_index != len(self.board_history) - 1:
            self.title.set("You can only make moves on the latest board state.")
            return

        self.goto(event)
        from_pos = self.selected
        to_pos = self.destination
        current_player = self.current_player()
        rolls_list = self.rolls.get().split()

        if not rolls_list:
            self.title.set("No dice rolls available to make a move.")
            return

        # Check if the move is valid
        try:
            used_die_value = current_player.move_piece(from_pos, to_pos, rolls_list)
            rolls_list.remove(str(used_die_value))  # Remove the used die
            self.rolls.set(' '.join(rolls_list))
            self.update_and_render_board()
        except ValueError as e:
            self.title.set(str(e))


        if not self.rolls.get():
            self.selected = None
            self.destination = None
            self.end_turn()
        else:
            self.title.set('Choose a piece to move')

    def select(self, event):
        x = event.x // TRI_WIDTH
        y = event.y // (TRI_HEIGHT + 1)  # Adjusted for correct calculation

        if y == 0:
            self.selected = 11 - x  # Top row positions 11 to 0
        elif y == 1:
            self.selected = get_captured_position(self.current_player().color)
        else:
            self.selected = x + 12  # Bottom row positions 12 to 23

        if self.current_player().color == WHITE:
            if self.selected == -1: # White captured pieces
                self.selected = 24
        else:
            if self.selected == 24: # Black captured pieces
                self.selected = 25
        #print(f"Source selected: {self.selected} (x={x}, y={y})")

    def goto(self, event):
        x = event.x // TRI_WIDTH
        y = event.y // (TRI_HEIGHT + 1)  # Adjusted for correct calculation

        if y == 0:
            self.destination = 11 - x  # Top row positions 11 to 0
        elif y == 1:
            self.destination = get_captured_position(self.current_player().color)
        else:
            self.destination = x + 12  # Bottom row positions 12 to 23

        if self.current_player().color == self.black.color:
            if self.destination == -1: # blacks escaped pieces
                self.destination = 27
        else:
            if self.destination == 24: # whites escaped pieces
                self.destination = 26   

        #print(f"Destination selected: {self.destination} (x={x}, y={y})")

    def current_player(self):
        return self.white if self.turn == WHITE else self.black

    def other_player(self):
        return self.black if self.turn == WHITE else self.white
       
    def prepare_turn(self):
        if DEBUG_MODE:
            print(f"{self.board}")
        current_player = self.current_player()

        if DEBUG_MODE:
                print(f"{current_player} turn started")

        if current_player.is_human:
            self.title.set(f"It's the {current_player} player's turn! Roll the dice!")
            self.rollButton.config(state=NORMAL)
            self.endButton.config(state=NORMAL)
        else:
            self.rollButton.config(state=DISABLED)
            self.endButton.config(state=DISABLED)
            self.AI_turn()

    def switch_turn(self):
        self.turn = WHITE if self.turn == BLACK else BLACK

    def end_turn(self):
        """Ends the current turn, re-enables the roll button, and resets UI."""
        self.auto_render = True  # Resume automatic rendering
        self.rolls.set('')
        self.time_remaining.set('')

        # Stop the timer to avoid confusion on next turn
        self.timer_running = False

        if self.check_win_condition():
            return # Do not proceed if the game is over

        self.switch_turn()
        self.prepare_turn()

    def check_win_condition(self):
        current_player = self.current_player()
        if current_player.win():
            print(f'{current_player} has won the game!')
            self.title.set(f'{current_player} has won the game!')

            self.rollButton.config(state=DISABLED)
            self.endButton.config(state=DISABLED)
            self._canvas.unbind('<Button-1>')
            self._canvas.unbind('<Button-3>')
            self.auto_render = False  # Stop automatic rendering

            # Update scores
            winner_idx = self.white_idx if self.turn == WHITE else self.black_idx
            self.scores[winner_idx] += 1

            if (NETWORK_TRAINING):
                boards_based_training(self.board_history)

            # Schedule the next game after a delay or end the session
            self.window.after(AI_DELAY, self.start_next_game)

            return True
        return False

    def update_and_render_board(self):
        # Update the board state and render it immediately
        self.board_history.append([self.board.copy(), self.turn])
        self.current_board_index += 1
        self.render_board(self.board)

    def show_previous_board(self):
        if self.current_board_index > 0:
            self.auto_render = False  # Pause automatic rendering
            self.current_board_index -= 1
            previous_board = self.board_history[self.current_board_index][0]
            self.render_board(previous_board)
        else:
            print("No previous board state available.")

    def show_next_board(self):
        if self.current_board_index < len(self.board_history) - 1:
            self.auto_render = False  # Pause automatic rendering
            self.current_board_index += 1
            next_board = self.board_history[self.current_board_index][0]
            self.render_board(next_board)
        else:
            print("No next board state available.")