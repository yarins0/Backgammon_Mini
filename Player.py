from typing import List
from BoardTree import BoardTree
from Constants import *

class Player:

    def __init__(self, 
                 color, 
                 board = START_BOARD, 
                 is_human=False):
        
        if color not in [BLACK, WHITE]:
            raise ValueError(f"Color must be {WHITE} or {BLACK}.")
        
        self.color = color
        self._is_human = is_human
        self.board = board
        self.pieces , self.other_pieces = self.convert_board_to_pieces_array(board)
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
    def win(self, board= None, color = None):
        if board is None:
            board = self.board
        if color is None:
            color = self.color
        # Check if the player has all 15 pieces borne off (escaped)
        return board[get_escaped_position(color)] == 15
    def get_next_player(self , color = None):
        if color is None:
            color = self.color
        return BLACK if color == WHITE else WHITE
    def move_piece(self, from_pos, to_pos, rolls):
        # Ensure rolls is a list of integers
        rolls = [int(value) for value in rolls]

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
        # Remove piece from the current position
        self.remove_piece(from_pos)
        # Add piece to the target position
        self.add_piece(to_pos)

        #self.pieces, self.other_pieces = self.convert_board_to_pieces_array(self.board)
        # Optionally return the used die value
        return used_die_value
            
    def valid_move(self, from_pos, to_pos, roll_values, board = None, current_color = None, simulate = False) -> bool:
        if board is None:
            board = self.board
        if current_color is None:
            current_color = self.color

        # Validate the move based on the board state
        if self.is_blocked(to_pos, board, current_color):
            if DEBUG_MODE and not simulate:
                print(f"Position {to_pos} is blocked")
            return False
        if not self.is_piece_at_position(from_pos, board, current_color):
            if DEBUG_MODE and not simulate:
                print(f"There is no piece at position {from_pos}")
            return False
        
        roll_values = [int(value) for value in roll_values]

        if from_pos == get_captured_position(current_color):
            move_distance = None
            for die_value in roll_values:
                expected_to_pos = die_value - 1 if current_color == WHITE else 24 - die_value
                if expected_to_pos == to_pos:
                    move_distance = die_value
                    break
            if move_distance is None:
                if DEBUG_MODE and not simulate:
                    print(f"No matching die value for this move from the bar to {to_pos}")
                return False
            
        elif to_pos == get_escaped_position(current_color):
            if not self.is_all_pieces_in_home(board, current_color):
                if DEBUG_MODE and not simulate:
                    print("All pieces must be in home to bear off")
                return False
            if not self.can_bear_off(from_pos, board, current_color):
                if DEBUG_MODE and not simulate:
                    print("Cannot bear off with this die")
                return False
            if not any(die >= from_pos + 1 for die in roll_values) and current_color == BLACK:
                if DEBUG_MODE and not simulate:
                    print(f"No matching die value for this move from {from_pos} to {to_pos}")
                return False
            if not any(die >= 24 - from_pos for die in roll_values) and current_color == WHITE:
                if DEBUG_MODE and not simulate:
                    print(f"No matching die value for this move from {from_pos} to {to_pos}")
                return False
            
        else:
            move_distance = to_pos - from_pos if current_color == WHITE else from_pos - to_pos

            if move_distance <= 0:
                if DEBUG_MODE and not simulate:
                    print(f"Invalid target position {to_pos}")
                return False
            
        return True
    
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

    def is_piece_at_position(self, position, board= None, color=None):
        # Check if there's a piece of the player's color at the position
        if color is None:
            color = self.color
        if board is None:
            board = self.board

        if color == WHITE or position > 23:
            return board[position] > 0
        else:
            return board[position] < 0
    
    def can_bear_off(self, from_pos, board = None, current_color = None):
        if board is None:
            board = self.board
        if current_color is None:
            current_color = self.color
            
        if current_color == WHITE:
            for pos in range(18, from_pos):
                if board[pos] > 0:
                    return False
        else:
            for pos in range(5, from_pos, -1):
                if board[pos] < 0:
                    return False
        return True
    
    def add_piece(self, position, board=None, color = None):
        if color is None:
            color = self.color
        if board is None:
            board = self.board

        if 0 <= position <= 23:
            if color == WHITE:
                board[position] += 1
            else:
                board[position] -= 1
        else:
            board[position] += 1  # Always increment by 1

    def remove_piece(self, position, board =None, color = None):
        if color is None:
            color = self.color
        if board is None:
            board = self.board

        if 0 <= position <= 23:
            if color == WHITE:
                board[position] -= 1
            else:
                board[position] += 1
        else:
            board[position] -= 1  # Always decrement by 1

    def count_pieces_on_board(self):
        total = 0
        for i in range(24):
            if self.is_piece_at_position(i):
                total += abs(self.board[i])
        return total
    
    def has_captured_piece(self, board=None, color= None):
        if board is None:
            board = self.board
        if color is None:
            color = self.color
        return board[get_captured_position(color)] > 0

    def capture_piece_at_position(self, position, board=None, color=None, simulate=False):
        if board is None:
            board = self.board
        if color is None:
            color = self.color
        if not self.is_opponent_vulnerable_at_position(position, board, color):
            return

        if DEBUG_MODE and not simulate:
            print(f"Capturing opponent piece at position {position}")
        # Remove the opponent's piece from the board
        opponent_color = self.get_next_player()
        self.remove_piece(position, board, opponent_color)

        # Place it on the bar (captured pieces)
        board[get_captured_position(opponent_color)] += 1

    def is_opponent_vulnerable_at_position(self, position, board=None, color=None):
        if board is None:
            board = self.board
        if color is None:
            color = self.color

        if position < 0 or position > 23:
            return False
        opponent_piece_count = self.board[position]
        return opponent_piece_count == 1 if self.color == BLACK else opponent_piece_count == -1

    def is_blocked(self, position, board= None, current_color=None):
        if position < 0 or position > 23:
            return False
        
        if current_color is None:
            current_color = self.color
        if board is None:
            board = self.board

        opponent_piece_count = board[position]
        result = opponent_piece_count >= 2 if self.color == BLACK else opponent_piece_count <= -2
        return result
    
    def is_all_pieces_in_home(self, board= None, current_color= None):
        if board is None:
            board = self.board
        if current_color is None:
            current_color = self.color

        if current_color == WHITE:
            for pos in range(18):
                if board[pos] > 0:
                    return False
        else:
            for pos in range(6,24):
                if board[pos] < 0:
                    return False
        return True

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
    
    def calculate_bearing_off_distance(self, from_pos):
        distance = 23 - from_pos + 1 if self.color == WHITE else from_pos + 1
        return distance

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
