from tkinter import *
from Player import *
from AI_Player import *
from Human_Player import *
from game_logic import *
from Constants import *

import random

TRI_HEIGHT = 200
TRI_WIDTH = 50

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
        self.black = AI_Player(self.BLACK, black_ratios) if black_player == self.AI else Human_Player(self.BLACK)
        self.white = AI_Player(self.WHITE, white_ratios) if white_player == self.AI else Human_Player(self.WHITE)

        self.white.set_other(self.black)
        self.black.set_other(self.white)

    def start_next_game(self):
        if self.current_game_index < len(self.players) * (len(self.players) - 1) // 2:
            i, j = self.get_player_indices(self.current_game_index)
            self.initialize_players(i, j)
            self.current_game_index += 1
            self.start_game()
        else:
            print("All games completed.")
            print("Scores:", self.scores)
            winner_idx = self.scores.index(max(self.scores))
            print(f"Overall winner: Player {winner_idx} with {self.scores[winner_idx]} wins")
            print(f"winners ratios: {self.players[winner_idx].ratios}")
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
            self.white.set_board_tree(BoardTree(self.board_history[self.current_board_index], 0.5))
            self.black.set_board_tree(BoardTree(self.board_history[self.current_board_index], 0.5))

        # Print starting game information
        black_type = "AI" if isinstance(self.black, AI_Player) else "Human"
        white_type = "AI" if isinstance(self.white, AI_Player) else "Human"
        print(f"Starting game between {white_type} player (white) and {black_type} player (black)")

        # Start the first turn with white
        self.turn = self.WHITE
        self.prepare_turn()

    def get_current_player_index(self):
        current_player = self.current_player()
        for idx, player in enumerate(self.players):
            # Compare the current player with players list to find the index
            if isinstance(current_player, AI_Player) and player[0] == self.AI and player[1] == current_player.ratios:
                return idx
            elif isinstance(current_player, Human_Player) and player == self.HUMAN:
                return idx
        return -1  # If not found

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
        
        :param player: The player input, which can be a string or a list.
        :return: A tuple containing the player type and ratios (if applicable).
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

        # Now create the labels with self.top_frame as the parent
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

        # The top_frame and labels are already created and packed in create_board

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

        # Bindings
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
            self.render_board(self.status_format())
        self._canvas.after(50, self.render)

    def render_board(self, board):
        self._canvas.delete('piece')
        # Render pieces based on the board state
        for position, count in enumerate(board):
            if count != 0:
                color = 'white' if count > 0 else 'black'
                count = abs(count)
                for pos in range(count):
                    if position < 12:
                        # Adjust the position calculation for the top row
                        self._canvas.create_oval((11 - position) * TRI_WIDTH, pos * TRI_WIDTH, (12 - position) * TRI_WIDTH,
                                                (pos + 1) * TRI_WIDTH, fill=color, tags='piece')
                    elif position < 24:
                        # Adjust the position calculation for the bottom row
                        self._canvas.create_oval((position - 12) * TRI_WIDTH, int(self._canvas.cget('height')) - ((pos + 1) * TRI_WIDTH),
                                                (position - 11) * TRI_WIDTH, int(self._canvas.cget('height')) - (pos * TRI_WIDTH),
                                                fill=color, tags='piece')
                    # Handle captured and out pieces
                    elif position == 24:  # White out
                        self._canvas.create_oval(0, pos * TRI_WIDTH, TRI_WIDTH, (pos + 1) * TRI_WIDTH, fill='white', tags='piece')
                    elif position == 25:  # Black out
                        self._canvas.create_oval(0, int(self._canvas.cget('height')) - ((pos + 1) * TRI_WIDTH),
                                                TRI_WIDTH, int(self._canvas.cget('height')) - (pos * TRI_WIDTH), fill='black', tags='piece')
                    elif position == 26:  # White captured
                        self._canvas.create_oval(12 * TRI_WIDTH, pos * TRI_WIDTH, 13 * TRI_WIDTH, (pos + 1) * TRI_WIDTH, fill='white', tags='piece')
                    elif position == 27:  # Black captured
                        self._canvas.create_oval(12 * TRI_WIDTH, int(self._canvas.cget('height')) - ((pos + 1) * TRI_WIDTH),
                                                13 * TRI_WIDTH, int(self._canvas.cget('height')) - (pos * TRI_WIDTH), fill='black', tags='piece')
        self._canvas.update_idletasks()  # Ensure the canvas is refreshed
    
    def humanMove1(self, event):
        if self.current_board_index != len(self.board_history) - 1:
            self.title.set("You can only make moves on the latest board state.")
            return

        self.select(event)
        piece = self.selected
        if piece not in self.current_player().get_pieces():
            self.title.set("That's an invalid piece to pick")
            return
        self.title.set('Choose a position to move it to (right click)')

    def humanMove2(self, event):
        if self.current_board_index != len(self.board_history) - 1:
            self.title.set("You can only make moves on the latest board state.")
            return

        self.goto(event)
        distance = self.destination - self.selected
        if self.turn == self.BLACK:
            distance = -distance
        rolls_list = self.rolls.get().split()

        current_player = self.current_player()

        if DEBUG_MODE:
            print(f"Debug: Selected piece: {self.selected}, Destination: {self.destination}, Distance: {distance}")
            print(f"Debug: Available rolls: {rolls_list}")

        if not rolls_list:
            self.title.set("No dice rolls available to make a move.")
            return

        # Check if the move is valid and the distance matches an available roll
        if current_player.valid_move(self.selected, self.destination, rolls_list) and str(abs(distance)) in rolls_list:
            try:
                current_player.move_piece(distance, self.selected, rolls_list)
                rolls_list.remove(str(abs(distance)))  # Remove the used die
                self.rolls.set(' '.join(rolls_list))
                self.update_and_render_board()
            except ValueError:
                self.title.set("Invalid move!")
        else:
            self.title.set("You can't move your piece there!")

        if not self.rolls.get():
            print(f"Ended human ({self.turn}) turn")
            self.end_turn()
        else:
            self.title.set('Choose a piece to move')

    def select(self, event):
        x = event.x // TRI_WIDTH
        y = event.y // TRI_HEIGHT

        if y == 0:
            self.selected = 12 - x
        elif y == 1:
            self.selected = 0
        else:
            self.selected = 13 + x

    def goto(self, event):
        x = event.x // TRI_WIDTH
        y = event.y // TRI_HEIGHT

        if y == 0:
            self.destination = 12 - x
        elif y == 1:
            self.destination = 0
        else:
            self.destination = 13 + x

    def current_player(self):
        return self.white if self.turn == self.WHITE else self.black

    def other_player(self):
        return self.black if self.turn == self.WHITE else self.white
    
    def check_win_condition(self):
        if self.current_player().win():
            winner_color = self.current_player().color
            self.title.set(f'{winner_color.capitalize()} has won the game!')

            self.rollButton.config(state=DISABLED)
            self.endButton.config(state=DISABLED)
            self._canvas.unbind('<Button-1>')
            self._canvas.unbind('<Button-3>')
            self.auto_render = False  # Stop automatic rendering

            # Update scores
            player_idx = self.get_current_player_index()
            self.scores[player_idx] += 1

            # Schedule the next game after a delay
            if self.current_game_index < len(self.players) * (len(self.players) - 1) // 2:
                self.window.after(2000, self.start_next_game)
            else:
                print("All games completed.")
                print("Scores:", self.scores)
                winner_idx = self.scores.index(max(self.scores))
                print(f"Overall winner: Player {winner_idx} with {self.scores[winner_idx]} wins")
                self.title.set(f"Overall winner: Player {winner_idx + 1} with {self.scores[winner_idx]} wins")

            return True
        return False
    
    def switch_turn(self):
        self.turn = self.WHITE if self.turn == self.BLACK else self.BLACK

    def end_turn(self):
        self.auto_render = True  # Resume automatic rendering
        self.rolls.set('')
        self.time_remaining.set('')

        if self.check_win_condition():
            return

        self.switch_turn()
        self.prepare_turn()

    def prepare_turn(self):
        if DEBUG_MODE:
            self.print_board(self.board_history[self.current_board_index])

        current_player = self.current_player()

        if current_player.isHuman():
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

        board = self.board_history[self.current_board_index]

        try:
            move_sequence = self.current_player().play(board, computer_roll)
            if move_sequence:
                for move in move_sequence:
                    # Execute each move
                    self.current_player().move_piece(abs(move[0] - move[1]), move[0], computer_roll)
                    self.update_and_render_board()
                    self.window.after(AI_DELAY)  # Optional: pause for Xms between moves

        except ValueError as e:
            print(e)
        except Exception as e:
            print(f"Unexpected error: {e}")

        print(f"Ended AI ({self.turn}) turn")
        self.window.after(2*AI_DELAY, self.end_turn)  # Schedule the end of the turn with a delay


    def print_board(self, board):
        print("Board:", board)
        print("White pieces:", self.white.get_pieces())
        print("Black pieces:", self.black.get_pieces())

    def status_format(self):
        return generate_board(self.white.get_pieces(), self.black.get_pieces())

    def update_and_render_board(self):
        # Update the board state and render it immediately
        board = self.status_format()
        self.board_history.append(board)
        self.current_board_index += 1
        if DEBUG_MODE:
            print(f"Updating board to: {board}")  # Debugging output
        self.render_board(board)
        if DEBUG_MODE:
            print("Board updated and rendered.")  # Debugging output

    def show_previous_board(self):
        if self.current_board_index > 0:
            self.auto_render = False  # Pause automatic rendering
            self.current_board_index -= 1
            previous_board = self.board_history[self.current_board_index]
            if DEBUG_MODE:
                print("Previous Board State:", previous_board)
            self.render_board(previous_board)
        else:
            print("No previous board state available.")

    def show_next_board(self):
        if self.current_board_index < len(self.board_history) - 1:
            self.auto_render = False  # Pause automatic rendering
            self.current_board_index += 1
            next_board = self.board_history[self.current_board_index]
            if DEBUG_MODE:
                print("Next Board State:", next_board)
            self.render_board(next_board)
        else:
            print("No next board state available.")


