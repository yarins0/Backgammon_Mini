from tkinter import *
from Player import Player
from AI_Player import AI_Player
from Human_Player import Human_Player
from game_logic import roll
from BoardTree import BoardTree
from Constants import *
import random

TRI_WIDTH = 50
TRI_HEIGHT = 200
class BackgammonGameGUI:
    AI = "AI"
    HUMAN = "Human"
    WHITE = "white"
    BLACK = "black"

    def __init__(self, window, players):
        self.window = window
        self.players = players
        self.scores = [0] * len(self.players)
        self.auto_render = True  # Flag to control automatic rendering
        self.current_game_index = 0  # Track the current game index

        # Initialize the first pair of players
        self.initialize_players(0, 1)

        # Initialize the UI components
        self.create_board()

        # Start the first game
        self.start_next_game()

    def initialize_players(self, i, j):
        black_player, black_ratios = self.parse_player(self.players[i])
        white_player, white_ratios = self.parse_player(self.players[j])

        # Initialize the game board
        self.board = START_BOARD

        # Create player instances with the shared board
        self.black = AI_Player(self.BLACK, self.board, black_ratios) if black_player == self.AI else Human_Player(self.BLACK, self.board)
        self.white = AI_Player(self.WHITE, self.board, white_ratios) if white_player == self.AI else Human_Player(self.WHITE, self.board)


    def start_next_game(self):
        if self.current_game_index < len(self.players) * (len(self.players) - 1) // 2:
            self.black_idx, self.white_idx = self.get_player_indices(self.current_game_index)
            self.initialize_players(self.black_idx, self.white_idx)
            self.current_game_index += 1
            self.start_game()
        else:
            # All games are completed
            print("All games completed.")
            print("Scores:", self.scores)
            winner_idx = self.scores.index(max(self.scores))
            winner_player = self.players[winner_idx]
            print(f"Overall winner: Player {winner_idx} with {self.scores[winner_idx]} wins")
            # Print the winner's ratios
            if winner_player[0] == self.AI:
                best_ratio = winner_player[1]
                print(f"The best ratio is: {best_ratio}")
            else:
                print("Winner is a human player.")

            self.title.set(f"Overall winner: Player {winner_idx + 1} with {self.scores[winner_idx]} wins")
            
    def start_game(self):
        print("Starting new game.")
        self.clear_board()

        # Initialize the board history
        self.board_history = []
        self.current_board_index = -1
        self.update_and_render_board()

        # Ensure that board history is initialized before accessing it
        if self.board_history:
            initial_board = self.board_history[self.current_board_index]
            self.white.set_board_tree(BoardTree(initial_board, 0.5))
            self.black.set_board_tree(BoardTree(initial_board, 0.5))

        # Print starting game information
        black_type = "AI" if not self.black.is_human else "Human"
        white_type = "AI" if not self.white.is_human else "Human"
        print(f"Starting game between {white_type} player (white) and {black_type} player (black)")

        # Start the first turn with white
        self.turn = self.WHITE
        self.prepare_turn()

    def get_player_indices(self, game_index):
        # Calculate player indices for the current game
        num_players = len(self.players)
        i = game_index // (num_players - 1)
        j = game_index % (num_players - 1)
        if j >= i:
            j += 1
        return i, j

    def parse_player(self, player):
        """
        Parse the player input to determine the type and ratios.
        """
        if isinstance(player, list) and len(player) == 2 and player[0] == self.AI:
            return self.AI, player[1]  # AI with specified ratios
        elif player == self.AI:
            return self.AI, EVAL_DISTRIBUTION  # AI with default ratios
        elif player == self.HUMAN:
            return self.HUMAN, None  # Human player
        else:
            raise ValueError("Invalid player input format")

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
            self.turn = self.WHITE

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
                space * TRI_WIDTH, int(self._canvas.cget('height')),
                (space + 1) * TRI_WIDTH, int(self._canvas.cget('height')),
                (space + 0.5) * TRI_WIDTH, int(self._canvas.cget('height')) - TRI_HEIGHT,
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
        self._canvas.bind('<Button-1>', self.humanMove1)
        self._canvas.bind('<Button-3>', self.humanMove2)

    def roll(self):
        self.r = roll()
        self.r.sort()
        rolled = ' '.join(map(str, self.r))
        self.rolls.set(rolled)
        self.rollButton.config(state=DISABLED)
        self.title.set('Choose a piece to move')
        self.start_timer()

    def start_timer(self):
        self.time_left = TURN_TIME
        self.update_timer()

    def update_timer(self):
        if self.time_left > 0:
            self.time_remaining.set(f"Time left: {self.time_left} seconds")
            self.time_left -= 1
            self.window.after(1000, self.update_timer)
        else:
            self.title.set("Time's up! Ending your turn.")
            self.end_turn()

    def render(self):
        if self.auto_render:
            # Render the board state
            self.render_board(self.board)
        self._canvas.after(50, self.render)

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

    def humanMove1(self, event):
        if self.current_board_index != len(self.board_history) - 1:
            self.title.set("You can only make moves on the latest board state.")
            return

        self.select(event)
        position = self.selected
        current_player = self.current_player()

        if not current_player.is_piece_at_position(position, current_player.color):
            self.title.set("That's an invalid piece to pick")
            return
        self.title.set('Choose a position to move it to (right click)')

    def humanMove2(self, event):
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
            print(f"Ended human ({self.turn}) turn")
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
            self.selected = self.current_player().get_captured_position()
        else:
            self.selected = x + 12  # Bottom row positions 12 to 23

        if self.current_player().color == self.white.color:
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
            self.destination = self.current_player().get_captured_position()
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
        return self.white if self.turn == self.WHITE else self.black

    def other_player(self):
        return self.black if self.turn == self.WHITE else self.white

    def check_win_condition(self):
        current_player = self.current_player()
        if current_player.win():
            winner_color = current_player.color
            self.title.set(f'{winner_color.capitalize()} has won the game!')

            self.rollButton.config(state=DISABLED)
            self.endButton.config(state=DISABLED)
            self._canvas.unbind('<Button-1>')
            self._canvas.unbind('<Button-3>')
            self.auto_render = False  # Stop automatic rendering

            # Update scores
            if self.current_player().color == self.WHITE:
                player_idx = self.white_idx
            else:
                player_idx = self.black_idx
            self.scores[player_idx] += 1

            # Schedule the next game after a delay or end the session
            self.window.after(AI_DELAY, self.start_next_game())

            return True
        return False

    def switch_turn(self):
        if DEBUG_MODE:
            print(f"{self.board}")
        self.turn = self.WHITE if self.turn == self.BLACK else self.BLACK

    def end_turn(self):
        self.auto_render = True  # Resume automatic rendering
        self.rolls.set('')
        self.time_remaining.set('')

        if self.check_win_condition():
            return # Do not proceed if the game is over

        self.switch_turn()
        self.prepare_turn()

    def prepare_turn(self):
        current_player = self.current_player()

        if current_player.is_human:
            self.title.set(f"It's the {current_player.color} player's turn! Roll the dice!")
            self.rollButton.config(state=NORMAL)
            self.endButton.config(state=NORMAL)
        else:
            print(f"AI ({current_player.color}) turn started")
            self.rollButton.config(state=DISABLED)
            self.endButton.config(state=DISABLED)
            self.AI_turn()

    def AI_turn(self):
        computer_roll = roll()
        print(f"Computer roll: {computer_roll}")

        # Convert the dice roll to strings before joining
        rolled = ' '.join(map(str, computer_roll))
        self.rolls.set(rolled)
        self.title.set(f"AI ({self.current_player().color}) rolled: {rolled}")

        #try:
        move_sequence = self.current_player().play(self.board , computer_roll)
        if move_sequence:
            for move in move_sequence:
                # Execute each move
                from_pos, to_pos = move
                self.current_player().move_piece(from_pos, to_pos, computer_roll)
                self.update_and_render_board()
                self.window.after(AI_DELAY)  # Optional: pause for AI_DELAY ms between moves

        print(f"Ended AI ({self.turn}) turn")
        self.window.after(2 * AI_DELAY, self.end_turn)  # Schedule the end of the turn with a delay

    def update_and_render_board(self):
        # Update the board state and render it immediately
        self.board_history.append(self.board.copy())
        self.current_board_index += 1
        self.render_board(self.board)

    def show_previous_board(self):
        if self.current_board_index > 0:
            self.auto_render = False  # Pause automatic rendering
            self.current_board_index -= 1
            previous_board = self.board_history[self.current_board_index]
            self.render_board(previous_board)
        else:
            print("No previous board state available.")

    def show_next_board(self):
        if self.current_board_index < len(self.board_history) - 1:
            self.auto_render = False  # Pause automatic rendering
            self.current_board_index += 1
            next_board = self.board_history[self.current_board_index]
            self.render_board(next_board)
        else:
            print("No next board state available.")