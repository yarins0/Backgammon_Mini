from Player import Player
from BoardTree import BoardTree, BoardNode
from Constants import *
from Eval_position import evaluate_position
import copy
from itertools import permutations

class AI_Player(Player):
    def __init__(self, color: str, board, ratios=EVAL_DISTRIBUTION):
        super().__init__(color, board, is_human=False)
        self.ratios = ratios
        # Initialize the board tree with the current board state
        self.board_tree = BoardTree(copy.deepcopy(self.board), evaluate_position(self.board, self.ratios))

    def play(self, roll: list) -> list:
        if CHOSEN_EVAL_METHOD == 1:
            return self.heuristic_play(roll)
        else:
            # Update the board tree root with the current board state
            self.board_tree.root.board = copy.deepcopy(self.board)
            self.board_tree.root.evaluation = evaluate_position(self.board, self.ratios)
            self.board_tree.root.path = []
            self.board_tree.root.player_turn = self.color
            self.board_tree.root.children = []  # Clear previous children

            # Ensure the tree is expanded to the required depth using the actual roll
            self.ensure_tree_depth(self.board_tree.root, MIN_MAX_DEPTH, current_roll=roll)

            executed_moves = self.strategic_play(roll, depth=MIN_MAX_DEPTH)

        return executed_moves

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

        # Start from the current root of the board tree
        current_node = self.board_tree.root

        for child in current_node.children:
            score = self.minimax(child, depth - 1)
            if (self.color == "white" and score > best_score) or (self.color == "black" and score < best_score):
                best_score = score
                best_move = child.path

        if best_move:
            print(f"Strategic AI ({self.color}) executed moves: {best_move} with score: {best_score}")
            return best_move
        else:
            print("No valid moves available for Strategic AI.")
            return []

    def minimax(self, node: BoardNode, depth: int) -> float:
        if depth == 0 or self.win_on_board(node.board):
            return evaluate_position(node.board, self.ratios)

        if node.player_turn == "white":
            max_eval = float('-inf')
            for child in node.children:
                eval = self.minimax(child, depth - 1)
                max_eval = max(max_eval, eval)
            return max_eval
        else:
            min_eval = float('inf')
            for child in node.children:
                eval = self.minimax(child, depth - 1)
                min_eval = min(min_eval, eval)
                return min_eval
            
    
    def ensure_tree_depth(self, node: BoardNode, depth: int, current_roll=None):
        if depth == 0:
            return

        if node.player_turn == self.color:
            if current_roll is None:
                print("Error: current_roll is None during AI's turn.")
                return
            # Use the actual roll when it's the AI's turn
            rolls_to_use = [current_roll]
        else:
            # Get all possible dice rolls for the opponent's turn
            rolls_to_use = self.get_possible_rolls()

        for roll in rolls_to_use:
            # Generate all possible moves from the current node for each roll
            all_moves = self.generate_all_moves(node.board, roll)
            if not all_moves:
                # If no moves are possible, create a child with the same board
                next_player_turn = self.other.color if node.player_turn == self.color else self.color
                new_node = BoardNode(
                    node.board,
                    evaluate_position(node.board, self.ratios),
                    [],
                    next_player_turn
                )
                node.add_child(new_node)
                # Recursively ensure depth for the new child
                self.ensure_tree_depth(new_node, depth - 1, current_roll)
            else:
                for moves in all_moves:
                    new_board = self.simulate_moves(copy.deepcopy(node.board), moves)

                    # Determine the next player's turn
                    next_player_turn = self.other.color if node.player_turn == self.color else self.color

                    new_node = BoardNode(
                        new_board,
                        evaluate_position(new_board, self.ratios),
                        moves,
                        next_player_turn
                    )
                    node.add_child(new_node)

                    # Recursively ensure depth for the new child
                    self.ensure_tree_depth(new_node, depth - 1, current_roll)

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
        self.generate_moves_recursive(board, roll, [], all_moves)
        return all_moves

    def generate_moves_recursive(self, board: list, rolls: list, move_sequence: list,
                                all_moves: list, pieces_on_bar: int = None):
        if pieces_on_bar is None:
            # Initialize the number of pieces on the bar for this recursion branch
            pieces_on_bar = board[self.get_captured_position()]

        if not rolls:
            all_moves.append(move_sequence)
            return

        possible_moves_found = False  # Flag to check if any moves were found in this call

        # Sort rolls to prioritize higher die
        sorted_rolls = sorted(rolls, reverse=True)

        for die_index, roll in enumerate(sorted_rolls):
            remaining_rolls = sorted_rolls[:die_index] + sorted_rolls[die_index + 1:]
            possible_moves = self.generate_valid_moves([roll], board)

            # Process possible moves using the helper function
            possible_moves_found = self.process_possible_moves(possible_moves, board, remaining_rolls,
                                        move_sequence, all_moves, pieces_on_bar)
            
        if not possible_moves_found:
            # No moves possible with any die
            all_moves.append(move_sequence)

    def process_possible_moves(self, possible_moves, board, remaining_rolls, move_sequence, all_moves, pieces_on_bar):
        if pieces_on_bar > 0:
            # Limit moves from the bar based on the number of pieces available
            possible_moves = [move for move in possible_moves if move[0] == self.get_captured_position()]
        else:
            # Exclude moves from the bar if no pieces are captured
            possible_moves = [move for move in possible_moves if move[0] != self.get_captured_position()]

        if possible_moves:
            for move in possible_moves:
                new_board = copy.deepcopy(board)
                self.simulate_move(new_board, move)

                new_pieces_on_bar = pieces_on_bar
                if move[0] == self.get_captured_position():
                    new_pieces_on_bar -= 1  # Decrement captured pieces

                # Continue recursion with remaining rolls
                self.generate_moves_recursive(
                    new_board,
                    remaining_rolls,
                    move_sequence + [move],
                    all_moves,
                    new_pieces_on_bar
                )
            return True  # Moves were found and processed
        return False  # No moves were found
    
                
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
        to_positions = []
        if from_pos == self.get_captured_position():
            # Re-entering from the bar
            to_pos = roll_value - 1 if self.color == "white" else 24 - roll_value
            to_positions.append(to_pos)
        else:
            # Regular move
            if self.color == 'white':
                to_pos = from_pos + roll_value
                if to_pos >= 24:
                    to_pos = self.get_escaped_position()
            else:
                to_pos = from_pos - roll_value
                if to_pos < 0:
                    to_pos = self.get_escaped_position()
            to_positions.append(to_pos)
        return to_positions

    def simulate_moves(self, board: list, moves: list) -> list:
        for move in moves:
            self.simulate_move(board, move)
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
        # Convert roll_values to integers if necessary
        roll_values = [int(value) for value in roll_values]

        if not isinstance(roll_values, list):
            print(f"Error: Expected roll_values to be a list, got {type(roll_values)}")
            return False

        # Check if the move is from the bar and there are captured pieces
        if from_pos == self.get_captured_position():
            if board[self.get_captured_position()] <= 0:
                return False  # No pieces to move from the bar
            move_distance = None
            for die_value in roll_values:
                expected_to_pos = die_value - 1 if self.color == "white" else 24 - die_value
                if expected_to_pos == to_pos:
                    move_distance = die_value
                    break
            if move_distance is None:
                return False
        else:
            # Regular move
            if self.color == 'white':
                move_distance = to_pos - from_pos
            else:
                move_distance = from_pos - to_pos

            if move_distance <= 0:
                return False

            if move_distance not in roll_values:
                # Check for bearing off with higher die
                if to_pos == self.get_escaped_position():
                    if not self.can_bear_off_from_position(from_pos, board):
                        return False
                    if not any(die >= move_distance for die in roll_values):
                        return False
                else:
                    return False

        # Validate the move destination
        if from_pos == self.get_captured_position():
            # Re-entering from the bar
            if self.is_blocked_on_board(to_pos, board):
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
        # Ensure there are no pieces on higher points
        if self.color == "white":
            for pos in range(18, position):
                if board[pos] > 0:
                    return False
        else:
            for pos in range(5, position, -1):
                if board[pos] < 0:
                    return False
        return True

    def is_blocked_on_board(self, position, board):
        if position < 0 or position > 23:
            return False
        opponent_piece_count = board[position]
        if self.other.color == "white":
            return opponent_piece_count >= 2
        else:
            return opponent_piece_count <= -2

    def all_pieces_in_home_board(self, board):
        if self.color == "white":
            for pos in range(0, 24):
                if board[pos] > 0 and pos < 18:
                    return False
        else:
            for pos in range(0, 24):
                if board[pos] < 0 and pos > 5:
                    return False
        return True

    def is_opponent_piece_at_position_on_board(self, position, board):
        if position < 0 or position > 23:
            return False
        opponent_piece_count = board[position]
        if self.other.color == "white":
            return opponent_piece_count > 0
        else:
            return opponent_piece_count < 0

    def capture_opponent_piece(self, board, position):
        # Remove the opponent's piece from the board
        self.other.remove_piece_from_board(board, position)
        # Place it on the bar (captured pieces)
        captured_position = self.other.get_captured_position()
        board[captured_position] += 1

    def add_piece_to_board(self, board, position):
        if position >= 0 and position <= 23:
            if self.color == "white":
                board[position] += 1
            else:
                board[position] -= 1
        else:
            # Bearing off or captured pieces
            board[position] += 1  # Always increment by 1

    def remove_piece_from_board(self, board, position):
        if position >= 0 and position <= 23:
            if self.color == "white":
                board[position] -= 1
            else:
                board[position] += 1
        else:
            # Bearing off or captured pieces
            board[position] -= 1  # Always decrement by 1

    def captured_piece_on_board(self, board):
        return board[self.get_captured_position()] > 0

    def is_piece_at_position_on_board(self, position, color, board):
        if color == "white":
            return board[position] > 0
        else:
            return board[position] < 0

    def win_on_board(self, board):
        # Check if the player has all 15 pieces borne off (escaped position)
        escaped_position = self.get_escaped_position()
        return abs(board[escaped_position]) == 15

    # Rest of the methods from AI_Player as needed