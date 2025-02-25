from tkinter import *
from Constants import *

if GUI_MODE:
    class BackgammonGameGUI:
        def __init__(self, window, BackgammonGame):
            self.backgammon_game = BackgammonGame
            self.window = window
            self.window.title("Backgammon Game")

            # Initialize the UI components
            self.create_board()

        
        def create_board(self):
            # Create the top frame first
            self.top_frame = Frame(self.window)
            self.top_frame.pack(pady=5)

            self.title = StringVar(value=f"")
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

            self.rollButton = Button(self.roll_frame, text='Roll', command=self.backgammon_game.roll)
            self.dieLabel = Label(self.roll_frame, textvariable=self.rolls, font=("Helvetica", 16))
            self.endButton = Button(self.roll_frame, text='End Turn (if stuck)', command=self.backgammon_game.end_turn)

            # Add buttons to navigate board history
            self.prevBoardButton = Button(self.roll_frame, text='<<', command=self.backgammon_game.show_previous_board)
            self.nextBoardButton = Button(self.roll_frame, text='>>', command=self.backgammon_game.show_next_board)

            self.setup_board_ui()

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
            self._canvas.bind('<Button-1>', self.backgammon_game.human_move1)
            self._canvas.bind('<Button-3>', self.backgammon_game.human_move2)

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

        def clear_board(self):
            # Clear the canvas content if it exists
            if hasattr(self, '_canvas'):
                self._canvas.delete('piece')  # Clear the pieces
                #self.draw_triangles()  # Redraw the triangles after clearing
            else:
                print("Canvas not initialized yet.")

            # Reset the UI components
            self.reset_components()

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
                self.set_title("Time's up! Ending your turn.")
                self.backgammon_game.end_turn()

        
        def select(self, event):
            x = event.x // TRI_WIDTH
            y = event.y // (TRI_HEIGHT + 1)  # Adjusted for correct calculation

            if y == 0:
                self.selected = 11 - x  # Top row positions 11 to 0
            elif y == 1:
                self.selected = self.backgammon_game.current_player().get_captured_position()
            else:
                self.selected = x + 12  # Bottom row positions 12 to 23

            if self.backgammon_game.turn == WHITE:
                if self.selected == -1: # White captured pieces
                    self.selected = 24
            else:
                if self.selected == 24: # Black captured pieces
                    self.selected = 25
            if DEBUG_MODE:
                print(f"Source selected: {self.selected} (x={x}, y={y})")

        def goto(self, event):
            x = event.x // TRI_WIDTH
            y = event.y // (TRI_HEIGHT + 1)  # Adjusted for correct calculation

            if y == 0:
                self.destination = 11 - x  # Top row positions 11 to 0
            elif y == 1:
                self.destination = self.backgammon_game.current_player().get_captured_position()
            else:
                self.destination = x + 12  # Bottom row positions 12 to 23

            if self.backgammon_game.turn == BLACK:
                if self.destination == -1: # blacks escaped pieces
                    self.destination = 27
            else:
                if self.destination == 24: # whites escaped pieces
                    self.destination = 26   

            if DEBUG_MODE:
                print(f"Destination selected: {self.destination} (x={x}, y={y})")

        def reset_movement(self):
            self.selected = None
            self.destination = None

        def disable_roll_button(self, disable =True):
            if disable:
                self.rollButton.config(state=DISABLED)
            else:
                self.rollButton.config(state=NORMAL)

        def disable_roll_end_buttons(self, disable = True):
            if disable:
                self.rollButton.config(state=DISABLED)
                self.endButton.config(state=DISABLED)
            else:
                self.rollButton.config(state=NORMAL)
                self.endButton.config(state=NORMAL)

        def disable_buttons(self):
            self.disable_roll_end_buttons()
            self._canvas.unbind('<Button-1>')
            self._canvas.unbind('<Button-3>')

        def reset_components(self):
            self.set_title("It's a new game! Roll the dice to start!")
            self.set_rolls()
            self.set_time_remaining()

        def set_title(self, title=''):
            self.title.set(title)

        def set_rolls(self, rolls=None):
            rolls_title= ' '
            if rolls:
                rolls_title = rolls_title.join(map(str, rolls))
            self.rolls.set(rolls_title)
            #self.rolls.set(''.join(chr(x) for x in rolls))

        def set_time_remaining(self, time=''):
            self.time_remaining.set(time)


else:
    class BackgammonGameGUI:
        def __init__(self, window, BackgammonGame):
            pass

        def create_board(self):
            pass

        def setup_board_ui(self):
            pass

        def draw_triangles(self):
            pass

        def render_board(self, board):
            pass

        def clear_board(self):
            pass

        def start_timer(self):
            pass

        def update_timer(self):
            pass

        def select(self, event):
            pass

        def goto(self, event):
            pass

        def reset_movement(self):
            pass

        def disable_roll_button(self, disable=True):
            pass
        
        def disable_roll_end_buttons(self, disable=True):
            pass

        def disable_buttons(self):
            pass

        def reset_components(self):
            pass

        def set_title(self, title=''):
            pass

        def set_rolls(self, rolls=None):
            pass

        def set_time_remaining(self, time=''):
            pass
