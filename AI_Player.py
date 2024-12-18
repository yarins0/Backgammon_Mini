from Player import Player
from Constants import *
from Eval_position import evaluate_position
import copy

class AI_Player(Player):
    def __init__(self, color: str, board, ratios=EVAL_DISTRIBUTION):
        super().__init__(color, board, is_human=False)
        self.ratios = ratios

    def play(self, roll: list) -> list:
        if CHOSEN_EVAL_METHOD == 1:
            return self.heuristic_play(roll)
        else:
            return self.strategic_play(roll, depth=MIN_MAX_DEPTH)

    def heuristic_play(self, roll: list) -> list:
        all_moves = self.generate_all_moves(self.board, roll)
        best_move, best_score = self.evaluate_moves(all_moves)

        if best_move:
            print(f"AI ({self.color}) executed moves: {best_move} with score: {best_score}")
            return best_move
        else:
            print("No valid moves available for AI.")
            return []

    def strategic_play(self, roll: list, depth: int = 2) -> list:
        best_score = float('-inf') if self.color == "white" else float('inf')
        best_move = None

        all_moves = self.generate_all_moves(self.board, roll)

        for moves in all_moves:
            new_board = self.simulate_moves(copy.deepcopy(self.board), moves)
            score = self.minimax(new_board, depth - 1, False)
            if (self.color == "white" and score > best_score) or (self.color == "black" and score < best_score):
                best_score = score
                best_move = moves

        if best_move:
            print(f"Strategic AI ({self.color}) executed moves: {best_move} with score: {best_score}")
            return best_move
        else:
            print("No valid moves available for Strategic AI.")
            return []

    def minimax(self, board: list, depth: int, is_maximizing_player: bool) -> float:
        if depth == 0 or self.win_on_board(board):
            return evaluate_position(board, self.ratios)

        if is_maximizing_player:
            max_eval = float('-inf')
            possible_rolls = self.get_possible_rolls()
            for roll in possible_rolls:
                all_moves = self.generate_all_moves(board, roll)
                for moves in all_moves:
                    new_board = self.simulate_moves(copy.deepcopy(board), moves)
                    eval = self.minimax(new_board, depth - 1, False)
                    max_eval = max(max_eval, eval)
            return max_eval
        else:
            min_eval = float('inf')
            possible_rolls = self.get_possible_rolls()
            for roll in possible_rolls:
                all_moves = self.generate_all_moves(board, roll)
                for moves in all_moves:
                    new_board = self.simulate_moves(copy.deepcopy(board), moves)
                    eval = self.minimax(new_board, depth - 1, True)
                    min_eval = min(min_eval, eval)
            return min_eval

    def get_possible_rolls(self) -> list:
        """
        Generate all unique dice roll combinations.
        :return: A list of unique dice roll combinations.
        """
        rolls = set()
        for i in range(1, 7):
            for j in range(1, 7):
                if i == j:
                    rolls.add((i, i, i, i))  # Doubles are played four times
                else:
                    rolls.add((i, j))
        return list(rolls)

    def evaluate_moves(self, all_moves):
        best_score = float('-inf') if self.color == "white" else float('inf')
        best_move = None

        for moves in all_moves:
            new_board = self.simulate_moves(copy.deepcopy(self.board), moves)
            score = evaluate_position(new_board, self.ratios)
            if (self.color == "white" and score > best_score) or (self.color == "black" and score < best_score):
                best_score = score
                best_move = moves

        return best_move, best_score

    def generate_all_moves(self, board: list, roll: list):
        all_moves = []
        if roll[0] != roll[-1]:
            # Include moves that starts with the second die if they are different
            self.generate_moves_recursive(board, roll[::-1], [], all_moves)
        self.generate_moves_recursive(board, roll, [], all_moves)
        print(f"AI ({self.color}) generated {len(all_moves)} moves for roll {roll}")
        print(all_moves)
        return all_moves
    
    def generate_moves_recursive(self, board: list, rolls: list, move_sequence: list, all_moves: list, pieces_on_bar: int = None):
        if pieces_on_bar is None:
            # Initialize the number of pieces on the bar for this recursion branch
            pieces_on_bar = board[self.get_captured_position()]

        if not rolls:
            all_moves.append(move_sequence)
            return

        roll = rolls[0]
        remaining_rolls = rolls[1:]

        possible_moves = self.generate_valid_moves([roll], board)

        if pieces_on_bar > 0:
            # Limit moves from the bar based on the number of pieces available
            possible_moves = [move for move in possible_moves if move[0] == self.get_captured_position()]
        else:
            # Exclude moves from the bar if no pieces are captured
            possible_moves = [move for move in possible_moves if move[0] != self.get_captured_position()]

        if possible_moves:
            for move in possible_moves:
                new_board = copy.deepcopy(board)
                valid_move = self.simulate_move(new_board, move)

                if new_board == board:
                    continue  # Move was invalid; skip

                new_pieces_on_bar = pieces_on_bar
                if move[0] == self.get_captured_position():
                    new_pieces_on_bar -= 1  # Decrement captured pieces

                self.generate_moves_recursive(new_board, remaining_rolls, move_sequence + [move], all_moves, new_pieces_on_bar)
        else:
            # Proceed to the next die even if no moves were found with the current die
            self.generate_moves_recursive(board, remaining_rolls, move_sequence, all_moves, pieces_on_bar)
                
    def generate_valid_moves(self, roll_values: list, board: list) -> list:
        if not isinstance(roll_values, list):
            print(f"Error: roll_values is not a list, it's {type(roll_values)}")
        moves = []
        captured_position = self.get_captured_position()

        # Use the board parameter to check for captured pieces
        if self.captured_piece_on_board(board):
            from_positions = [captured_position]
        else:
            # Positions where the player has pieces
            from_positions = [
                i for i in range(24) if self.is_piece_at_position_on_board(i, self.color, board)
            ]

        for from_pos in from_positions:
            for die in roll_values:
                possible_to_positions = self.calculate_possible_to_positions(from_pos, die, board)
                for to_pos in possible_to_positions:
                    if self.valid_move_with_board(from_pos, to_pos, [die], board):
                        moves.append((from_pos, to_pos))
        return moves

    def calculate_possible_to_positions(self, from_pos, roll_value, board):
        possible_to_positions = []

        if from_pos == self.get_captured_position():
            # Re-entering from the bar
            if self.color == "white":
                to_pos = roll_value - 1  # Positions 0-5 correspond to rolls 1-6
            else:  # black
                to_pos = 24 - roll_value  # Positions 23-18 correspond to rolls 1-6
            # Check if the position is not blocked
            if not self.is_blocked_on_board(to_pos, board):
                possible_to_positions.append(to_pos)
        else:
            # Regular move logic
            if self.color == "white":
                to_pos = from_pos + roll_value
                # Check for bearing off
                if to_pos >= 24:
                    if self.can_bear_off(from_pos):
                        to_pos = self.get_escaped_position()
                    else:
                        return possible_to_positions  # No valid moves
            else:  # black
                to_pos = from_pos - roll_value
                # Check for bearing off
                if to_pos < 0:
                    if self.can_bear_off(from_pos):
                        to_pos = self.get_escaped_position()
                    else:
                        return possible_to_positions  # No valid moves

            # Check if the move is not blocked
            if not self.is_blocked_on_board(to_pos, board):
                possible_to_positions.append(to_pos)

        return possible_to_positions

    def simulate_moves(self, board: list, moves: list) -> list:
        for move in moves:
            board = self.simulate_move(board, move)
        return board
    def simulate_move(self, board: list, move: tuple) -> list:
        from_pos, to_pos = move

        # Check if there is a piece to move from 'from_pos'
        if from_pos == self.get_captured_position():
            if board[from_pos] <= 0:
                print(f"No captured pieces to move from position {from_pos}")
                return board  # Do not proceed with the move
            board[from_pos] -= 1  # Decrement captured pieces
        else:
            # Ensure there's a piece to move
            if self.is_piece_at_position_on_board(from_pos, self.color, board):
                self.remove_piece_from_board(board, from_pos)
            else:
                print(f"No piece at position {from_pos} to move")
                return board  # Do not proceed with the move

        # Handle capturing opponent's piece at to_pos
        if self.is_opponent_piece_at_position_on_board(to_pos, board):
            self.capture_opponent_piece(board, to_pos)

        # Add piece to to_pos
        self.add_piece_to_board(board, to_pos)

        return board

    def valid_move_with_board(self, from_pos, to_pos, roll_values, board):
        """
        Validates a move on the given board, considering the die values.

        :param from_pos: The starting position of the piece.
        :param to_pos: The target position of the piece.
        :param roll_values: A list of die values (e.g., [3, 5]).
        :param board: The current board state.
        :return: True if the move is valid, False otherwise.
        """
        # If the player has captured pieces, they must move them first
        if self.captured_piece_on_board(board) and from_pos != self.get_captured_position():
            return False  # Must move captured pieces first

        # Determine move distance
        if from_pos == self.get_captured_position():
            # Re-entering from the bar
            move_distance = self.calculate_reentry_move_distance(to_pos)
        elif to_pos == self.get_escaped_position():
            # Bearing off
            move_distance = self.calculate_bearing_off_distance(from_pos)
        else:
            # Regular move
            move_distance = abs(to_pos - from_pos)
            if self.color == 'black':
                move_distance = abs(from_pos - to_pos)  # Adjust for black's direction

        # Check if the move distance matches any of the dice roll values
        if move_distance in roll_values:
            die_used = move_distance
        elif to_pos == self.get_escaped_position():
            # Allow bearing off with a higher die if there are no pieces behind
            higher_die_values = [die for die in roll_values if die > move_distance]
            if higher_die_values and self.can_bear_off_from_position(from_pos, board):
                die_used = min(higher_die_values)  # Use the smallest higher die
            else:
                return False  # Cannot bear off with a die not matching move distance
        else:
            return False  # Move distance does not match any die roll

        # Validate the move destination
        if from_pos == self.get_captured_position():
            # Re-entering from the bar
            if not self.can_enter_from_bar(to_pos, board):
                return False  # Cannot enter if the point is blocked
        elif to_pos == self.get_escaped_position():
            # Bearing off
            if not self.all_pieces_in_home_board(board):
                return False  # Cannot bear off until all pieces are in home board
            if not self.can_bear_off_from_position(from_pos, board):
                return False  # There are pieces behind this position
        elif to_pos < 0 or to_pos > 23:
            return False  # Destination is outside of the board
        elif self.is_blocked_on_board(to_pos, board):
            return False  # Destination is blocked by opponent's pieces

        # Move is valid
        return True

    def can_bear_off_from_position(self, position, board):
        home_range = range(18, 24) if self.color == "white" else range(0, 6)
        if self.color == 'white':
            for i in home_range:
                if self.is_piece_at_position_on_board(i, self.color, board) and i < position:
                    return False
        else:
            for i in home_range:
                if self.is_piece_at_position_on_board(i, self.color, board) and i > position:
                    return False
        return True

    def calculate_reentry_move_distance(self, to_pos):
        if self.color == 'white':
            return to_pos + 1  # Positions 0-5 correspond to rolls 1-6
        else:
            return 24 - to_pos  # Positions 23-18 correspond to rolls 1-6
        
    def can_enter_from_bar(self, position, board):
        # For white, positions 0-5 are the opponent's home board
        # For black, positions 18-23 are the opponent's home board
        if self.color == "white":
            if position < 0 or position > 5:
                return False
        else:
            if position < 18 or position > 23:
                return False
        # Check if the position is not blocked by two or more opponent's pieces
        return not self.is_blocked_on_board(position, board)

    def is_blocked_on_board(self, position, board):
        if position < 0 or position > 23:
            return False
        opponent_color = "white" if self.color == "black" else "black"
        if opponent_color == "white":
            return board[position] >= 2
        else:
            return board[position] <= -2

    def all_pieces_in_home_board(self, board):
        home_range = range(18, 24) if self.color == "white" else range(0, 6)
        for i in range(24):
            if self.is_piece_at_position_on_board(i, self.color, board) and i not in home_range:
                return False
        return True

    def is_opponent_piece_at_position_on_board(self, position, board):
        opponent_color = "white" if self.color == "black" else "black"
        if opponent_color == "white":
            return board[position] > 0
        else:
            return board[position] < 0

    def capture_opponent_piece(self, board, position):
        opponent_captured_pos = self.other.get_captured_position()
        # Remove opponent's piece from the board
        self.other.remove_piece_from_board(board, position)
        # Add opponent's piece to their captured position
        self.other.add_piece_to_board(board, opponent_captured_pos)

    def add_piece_to_board(self, board, position):
        if position >= 0 and position <= 23:
            if self.color == "white":
                board[position] += 1
            else:
                board[position] -= 1
        else:
            board[position] += 1  # Positions 24-27

    def remove_piece_from_board(self, board, position):
        if position >= 0 and position <= 23:
            if self.color == "white":
                board[position] -= 1
            else:
                board[position] += 1
        else:
            board[position] -= 1  # Positions 24-27

    def captured_piece_on_board(self, board):
        captured_position = self.get_captured_position()
        return board[captured_position] > 0

    def is_piece_at_position_on_board(self, position, color, board):
        if color == "white":
            return board[position] > 0
        else:
            return board[position] < 0

    def win_on_board(self, board):
        # Check if the player has all 15 pieces borne off (position 26 or 27)
        escaped_position = self.get_escaped_position()
        return abs(board[escaped_position]) == 15