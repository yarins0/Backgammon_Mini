from typing import List
from BoardTree import BoardTree
from Constants import *

class Player:
    def __init__(self, color, board, is_human=False):
        if color not in ["black", "white"]:
            raise ValueError("Color must be 'black' or 'white'.")
        self.color = color
        self._is_human = is_human
        self.board = board
        self.board_tree = None
        self.other = None  # Will be set using set_other method

    @property
    def is_human(self):
        return self._is_human
    
    def play(self, roll):
        pass  # Implement the logic for playing a turn

    def set_board_tree(self, board_tree):
        self.board_tree = board_tree

    def set_other(self, other):
        self.other = other

    def win(self):
        # Check if the player has all 15 pieces borne off (escaped)
        return self.board[self.get_escaped_position()] == 15

    def lose(self):
        # Return True if the opponent has no pieces left on the board
        return self.board[self.other.get_escaped_position()] == 15

    def move_piece(self, from_pos, to_pos, rolls):
        # Ensure rolls is a list of integers
        rolls = [int(value) for value in rolls]

        # Validate that the piece to move is valid
        if from_pos != self.get_captured_position() and not self.is_piece_at_position(from_pos, self.color):
            raise ValueError('The chosen piece is not valid')

        # If the player has captured pieces, they must move them first
        if self.captured_piece() and from_pos != self.get_captured_position():
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

        # Update the board tree if using evaluation method 2
        if CHOSEN_EVAL_METHOD == 2:
            if not self.is_human:
                self.update_board_tree([from_pos, to_pos])
            if self.other and not self.other.is_human:
                self.other.update_board_tree([from_pos, to_pos])

        # Optionally return the used die value
        return used_die_value

    def is_move_distance_valid(self, from_pos, to_pos, die_value):
        # Checks if a specific die value allows moving from from_pos to to_pos
        if from_pos == self.get_captured_position():
            # Re-entering from the bar
            expected_to_pos = die_value - 1 if self.color == "white" else 24 - die_value
            return expected_to_pos == to_pos
        else:
            if self.color == 'white':
                expected_to_pos = from_pos + die_value
                if expected_to_pos >= 24:
                    expected_to_pos = self.get_escaped_position()
            else:
                expected_to_pos = from_pos - die_value
                if expected_to_pos < 0:
                    expected_to_pos = self.get_escaped_position()
            return expected_to_pos == to_pos
            
    def valid_move(self, from_pos: int, to_pos: int, rolls: list) -> bool:
        # Convert rolls to integers if necessary
        rolls = [int(value) for value in rolls]

        if not isinstance(rolls, list):
            raise TypeError(f"Expected rolls to be a list, got {type(rolls)}")

        # If the player has captured pieces, they must move them first
        if self.captured_piece() and from_pos != self.get_captured_position():
            print("Must move captured piece first")
            return False  # Must move captured pieces first

        # Determine if the move can be made with any of the dice rolls
        for die in rolls:
            if self.is_move_distance_valid(from_pos, to_pos, die):
                # Additional checks for blocked positions
                if to_pos == self.get_escaped_position():
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
        home_range = range(18, 24) if self.color == "white" else range(0, 6)
        for i in home_range:
            if self.is_piece_at_position(i, self.color):
                if (self.color == "white" and i < from_pos) or (self.color == "black" and i > from_pos):
                    return False
        return True

    def update_board(self, from_pos, to_pos):
        # Remove piece from the current position
        self.remove_piece(from_pos)
        # Add piece to the target position
        self.add_piece(to_pos)

    def is_piece_at_position(self, position, color):
        # Check if there's a piece of the player's color at the position
        return self.board[position] > 0 if color == "white" else self.board[position] < 0

    def add_piece(self, position):
        if position >= 0 and position <= 23:
            if self.color == "white":
                self.board[position] += 1
            else:
                self.board[position] -= 1
        else:
            self.board[position] += 1  # Always increment by 1

    def add_piece_to_board(self, board, position):
        if position >= 0 and position <= 23:
            if self.color == "white":
                board[position] += 1
            else:
                board[position] -= 1
        else:
            board[position] += 1  # Always increment by 1

    def remove_piece(self, position):
        if position >= 0 and position <= 23:
            if self.color == "white":
                self.board[position] -= 1
            else:
                self.board[position] += 1
        else:
            self.board[position] -= 1  # Always decrement by 1

    def remove_piece_from_board(self, board, position):
        if position >= 0 and position <= 23:
            if self.color == "white":
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
        return self.board[self.get_captured_position()] > 0

    def capture_piece_at_position(self, position):
        if self.is_opponent_vulnerable_at_position(position):
            print(f"Capturing opponent piece at position {position}")
            # Remove the opponent's piece from the board
            self.other.remove_piece(position)
            # Place it on the bar (captured pieces)
            self.board[self.other.get_captured_position()] += 1

    def is_opponent_vulnerable_at_position(self, position):
        if position < 0 or position > 23:
            return False
        opponent_piece_count = self.board[position]
        return opponent_piece_count == 1 if self.other.color == "white" else opponent_piece_count == -1

    def is_blocked(self, position):
        if position < 0 or position > 23:
            return False
        opponent_piece_count = self.board[position]
        result = opponent_piece_count >= 2 if self.other.color == "white" else opponent_piece_count <= -2
        return result

    def all_pieces_in_home(self):
        home_range = range(18, 24) if self.color == "white" else range(0, 6)
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
        if self.color == 'white' and expected_to_pos >= 24:
            expected_to_pos = self.get_escaped_position()
        elif self.color == 'black' and expected_to_pos < 0:
            expected_to_pos = self.get_escaped_position()

        if expected_to_pos == to_pos:
            return die_value
        else:
            return None

    def calculate_target_position(self, from_pos, distance):
        if self.color == "white":
            target = from_pos + distance
            if target >= 24:
                target = self.get_escaped_position()
        else:
            target = from_pos - distance
            if target < 0:
                target = self.get_escaped_position()
        return target

    def calculate_target_distance(self, from_pos, to_pos):
        if self.color == "white":
            distance = to_pos - from_pos
            if to_pos == self.get_escaped_position():
                distance = 23 - from_pos + 1
        else:
            distance = from_pos - to_pos
            if to_pos == self.get_escaped_position():
                distance = from_pos + 1
        return distance
    
    def is_bearing_off_position(self, position):
        result = position == self.get_escaped_position()
        return result

    def get_captured_position(self):
        position = 24 if self.color == "white" else 25
        return position

    def get_escaped_position(self):
        position = 26 if self.color == "white" else 27
        return position

    def update_board_tree(self, move):
        # Implement the board tree update logic here
        pass