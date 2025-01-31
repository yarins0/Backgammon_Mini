from typing import List
from BoardTree import BoardTree
from Constants import *

class Player:

    def __init__(self, 
                 color, 
                 board = START_BOARD, 
                 is_human=False):
        
        if color not in [BLACK, WHITE]:
            raise ValueError("Color must be 'black' or 'white'.")
        
        self.color = color
        self._is_human = is_human
        self.board = board
        self.pieces , self.other_pieces = self.convert_board_to_pieces_array(self.board)
        self.board_tree = None

    @property
    def is_human(self):
        return self._is_human
    
    def play(self, board, roll, color = None, time = 0):
        pass  # Implement the logic for playing a turn

    def play_random(self, board, roll, color, time):
        self.play(board, roll, color, time)

    def convert_board_to_pieces_array(self, board):
        pieces = []  # Reset current player pieces
        other_pieces = []  # Reset opposing player pieces

        # Populate self._pieces and self.other_pieces based on board state
        # the first 24
        for i in range(len(board) - 4):
            if board[i] > 0:  # White pieces
                if self.color == WHITE:
                    pieces.extend([i + 1] * board[i])
                else:
                    other_pieces.extend([i + 1] * board[i])
            elif board[i] < 0:  # Black pieces
                if self.color == BLACK:
                    pieces.extend([i + 1] * abs(board[i]))
                else:
                    other_pieces.extend([i + 1] * abs(board[i]))

        # the last 4
        if self.color == BLACK:
            pieces.extend([0] * abs(board[25]))
            pieces.extend([25] * abs(board[27]))
            other_pieces.extend([25] * abs(board[24]))
            other_pieces.extend([0] * abs(board[26]))

        elif self.color == WHITE:
            other_pieces.extend([0] * board[25])
            other_pieces.extend([25] * board[27])
            pieces.extend([25] * board[24])
            pieces.extend([0] * board[26])

        pieces.sort()  # Ensure pieces are ordered
        other_pieces.sort()

        return pieces, other_pieces

    def set_pieces(self, pieces):
        self.pieces = pieces
    
    def set_other_pieces(self, other_pieces): 
        self.other_pieces = other_pieces
    
    def get_pieces(self):
        return self.pieces
    
    def get_other_pieces(self):
        return self.other_pieces
    
    def set_board_tree(self, board_tree):
        self.board_tree = board_tree
    def win(self):
        # Check if the player has all 15 pieces borne off (escaped)
        return self.board[get_escaped_position(self.color)] == 15  
    def get_next_player(self , color = None):
        if color is None:
            color = self.color
        return BLACK if color == WHITE else WHITE

    def move_piece(self, from_pos, to_pos, rolls):
        # Ensure rolls is a list of integers
        rolls = [int(value) for value in rolls]

        # Validate that the piece to move is valid
        if from_pos != get_captured_position(self.color) and not self.is_piece_at_position(from_pos, self.color):
            raise ValueError('The chosen piece is not valid')

        # If the player has captured pieces, they must move them first
        if self.captured_piece() and from_pos != get_captured_position(self.color):
            raise ValueError('You must move your captured piece first')

        # Validate the move
        if not self.valid_move(from_pos, to_pos, rolls):
            raise ValueError('That is an invalid place to move your piece')

        # Determine the die value used for this move
        used_die_value = None
        for die in rolls:
            if self.is_move_distance_valid(from_pos, to_pos, die):
                used_die_value = die
                break

        if used_die_value is None:
            raise ValueError('No matching die value for this move')

        # Handle capturing opponent's pieces before moving
        self.capture_piece_at_position(to_pos)

        # Update the board
        self.update_board(from_pos, to_pos)

        #self.pieces, self.other_pieces = self.convert_board_to_pieces_array(self.board)
        # Optionally return the used die value
        return used_die_value

    def is_move_distance_valid(self, from_pos, to_pos, die_value):
        # Checks if a specific die value allows moving from from_pos to to_pos
        if from_pos == get_captured_position(self.color):
            # Re-entering from the bar
            expected_to_pos = die_value - 1 if self.color == WHITE else 24 - die_value
            return expected_to_pos == to_pos
        else:
            if self.color == WHITE:
                expected_to_pos = from_pos + die_value
                if expected_to_pos >= 24:
                    expected_to_pos = get_escaped_position(self.color)
            else:
                expected_to_pos = from_pos - die_value
                if expected_to_pos < 0:
                    expected_to_pos = get_escaped_position(self.color)
            return expected_to_pos == to_pos
            
    def valid_move(self, from_pos: int, to_pos: int, rolls: list) -> bool:
        # Convert rolls to integers if necessary
        rolls = [int(value) for value in rolls]

        if not isinstance(rolls, list):
            raise TypeError(f"Expected rolls to be a list, got {type(rolls)}")

        # If the player has captured pieces, they must move them first
        if self.captured_piece() and from_pos != get_captured_position(self.color):
            print("Must move captured piece first")
            return False  # Must move captured pieces first

        # Determine if the move can be made with any of the dice rolls
        for die in rolls:
            if self.is_move_distance_valid(from_pos, to_pos, die):
                # Additional checks for blocked positions
                if to_pos == get_escaped_position(self.color):
                    if not self.all_pieces_in_home():
                        print("All pieces must be in home to bear off")
                        return False
                    # Allow bearing off with a higher die
                    if self.calculate_target_distance(from_pos, to_pos) == die or self.can_bear_off(from_pos):
                        return True
                    else:
                        print("Cannot bear off with this die")
                        return False                    
                elif to_pos < 0 or to_pos > 23:
                    print("Invalid target position")
                    return False
                elif self.is_blocked(to_pos):
                    print(f"Position {to_pos} is blocked")
                    return False
                else:
                    # Move is valid
                    return True

        print(f"No valid die for move from {from_pos} to {to_pos} with rolls {rolls}")
        return False
    
    def calculate_bearing_off_distance(self, from_pos):
        distance = 23 - from_pos + 1 if self.color == 'white' else from_pos + 1
        return distance

    def can_bear_off(self, from_pos):
        # Ensure there are no pieces on higher points
        home_range = range(18, 24) if self.color == WHITE else range(0, 6)
        for i in home_range:
            if self.is_piece_at_position(i, self.color):
                if (self.color == WHITE and i < from_pos) or (self.color == BLACK and i > from_pos):
                    return False
        return True

    def update_board(self, from_pos, to_pos):
        # Remove piece from the current position
        self.remove_piece(from_pos)
        # Add piece to the target position
        self.add_piece(to_pos)

    def is_piece_at_position(self, position, color):
        # Check if there's a piece of the player's color at the position
        return self.board[position] > 0 if color == WHITE else self.board[position] < 0

    def add_piece(self, position):
        if position >= 0 and position <= 23:
            if self.color == WHITE:
                self.board[position] += 1
            else:
                self.board[position] -= 1
        else:
            self.board[position] += 1  # Always increment by 1

    def add_piece_to_board(self, board, position):
        if position >= 0 and position <= 23:
            if self.color == WHITE:
                board[position] += 1
            else:
                board[position] -= 1
        else:
            board[position] += 1  # Always increment by 1

    def remove_piece(self, position):
        if position >= 0 and position <= 23:
            if self.color == WHITE:
                self.board[position] -= 1
            else:
                self.board[position] += 1
        else:
            self.board[position] -= 1  # Always decrement by 1

    def remove_piece_from_board(self, board, position, color = None):
        if color is None:
            color = self.color

        if position >= 0 and position <= 23:
            if color == WHITE:
                board[position] -= 1
            else:
                board[position] += 1
        else:
            board[position] -= 1  # Always decrement by 1

    def count_pieces_on_board(self):
        total = 0
        for i in range(24):
            if self.is_piece_at_position(i, self.color):
                total += abs(self.board[i])
        return total

    def captured_piece(self):
        return self.board[get_captured_position(self.color)] > 0

    def capture_piece_at_position(self, position):
        if self.is_opponent_vulnerable_at_position(position):
            if DEBUG_MODE:
                print(f"Capturing opponent piece at position {position}")
            # Remove the opponent's piece from the board
            opponent_color = self.get_next_player()
            self.remove_piece_from_board(self.board, position , opponent_color)

            # Place it on the bar (captured pieces)
            self.board[get_captured_position(opponent_color)] += 1

    def is_opponent_vulnerable_at_position(self, position):
        if position < 0 or position > 23:
            return False
        opponent_piece_count = self.board[position]
        return opponent_piece_count == 1 if self.color == BLACK else opponent_piece_count == -1

    def is_blocked(self, position):
        if position < 0 or position > 23:
            return False
        opponent_piece_count = self.board[position]
        result = opponent_piece_count >= 2 if self.color == BLACK else opponent_piece_count <= -2
        return result

    def all_pieces_in_home(self):
        home_range = range(18, 24) if self.color == WHITE else range(0, 6)
        for i in range(24):
            if self.is_piece_at_position(i, self.color) and i not in home_range:
                return False
        return True

    def calculate_move_distance(self, from_pos, to_pos, die_value):
        # Calculates the move distance based on die_value and player color
        if self.color == 'white':
            expected_to_pos = from_pos + die_value
        else:
            expected_to_pos = from_pos - die_value

        # Adjust for bearing off
        if (self.color == 'white' and expected_to_pos >= 24) or (self.color == 'black' and expected_to_pos < 0):
            expected_to_pos = get_escaped_position(self.color)

        if expected_to_pos == to_pos:
            return die_value
        else:
            return None

    def calculate_target_position(self, from_pos, distance, color = None):
        if color is None:
            color = self.color

        if color == WHITE:
            target = from_pos + distance
            if target >= 24:
                target = get_escaped_position(color)
            if from_pos == get_captured_position(color):
                target = distance - 1
        else:
            target = from_pos - distance
            if target < 0:
                target = get_escaped_position(color)
            if from_pos == get_captured_position(color):
                target = 24 - distance
        return target

    def calculate_target_distance(self, from_pos, to_pos, color = None):
        if color is None:
            color = self.color
            
        if self.color == WHITE:
            distance = to_pos - from_pos
            if to_pos == get_escaped_position(color):
                distance = 23 - from_pos + 1
            if from_pos == get_captured_position(color):
                distance = to_pos + 1
        else:
            distance = from_pos - to_pos
            if to_pos == get_escaped_position(color):
                distance = from_pos + 1
            if from_pos == get_captured_position(color):
                distance = 24 - to_pos
        return distance
    
    def is_bearing_off_position(self, position):
        return position == get_escaped_position()
    
def get_captured_position(color=None):
    """
    Return the captured (bar) position for the given color.
    If color is not provided, defaults to self.color.
    """
    if color is None:
        color = color
    return 24 if color == WHITE else 25

def get_escaped_position(color=None):
    """
    Return the escaped (borne off) position for the given color.
    If color is not provided, defaults to self.color.
    """
    if color is None:
        color = color
    return 26 if color == WHITE else 27
