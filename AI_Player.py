from Player import *
from Constants import *
from Eval_position import evaluate_position
import copy



class AI_Player(Player):
    def __init__(self, color: str, ratios=EVAL_DISTRIBUTION):
        super().__init__(color)
        self.validate_ratios(ratios)
        self.ratios = ratios

    @staticmethod
    def validate_ratios(ratios):
        if len(ratios) != 5:
            raise ValueError("Ratios dictionary must contain exactly 5 elements.")
        if not abs(sum(ratios.values()) - 1.0) < 1e-6:
            raise ValueError("The sum of the ratios must be 1.")
    

    def isHuman(self) -> bool:
        return False

    def play(self, board: list, roll: list) -> list:
        
        self.initialize_pieces_from_board(board)
            
        if CHOSEN_EVAL_METHOD == 1:
            return self.heuristic_play(board, roll)
        else:
            # Ensure the tree is expanded to the required depth
            self.ensure_tree_depth(self.board_tree.root, MIN_MAX_DEPTH)
            return self.strategic_play(board, roll, depth=MIN_MAX_DEPTH)

    def heuristic_play(self, board: list, roll: list) -> list:
        all_boards = self.generate_all_boards(board, roll)
        best_move, best_score = self.evaluate_moves(all_boards, roll)

        if best_move:
            print(f"AI ({self.color}) executed moves: {best_move} with score: {best_score}")
            return best_move
        else:
            print("No valid moves available for AI.")
            return []


    def strategic_play(self, board: list, roll: list, depth: int = 2) -> list:
        best_score = float('-inf') if self.color == "white" else float('inf')
        best_move = None

        all_boards = self.generate_all_boards(board, roll)

        for new_board, move_sequence in all_boards:
            score = self.minimax(new_board, depth - 1, False)
            if (self.color == "white" and score > best_score) or (self.color == "black" and score < best_score):
                best_score = score
                best_move = move_sequence

        if best_move:
            print(f"Strategic AI ({self.color}) executed moves: {best_move} with score: {best_score}")
            return best_move
        else:
            print("No valid moves available for Strategic AI.")
            return []

    def minimax(self, board: list, depth: int, is_maximizing: bool) -> float:
        if depth == 0 or self.win():
            return evaluate_position(board, self.ratios)

        if is_maximizing:
            max_eval = float('-inf')
            possible_rolls = self.get_possible_rolls()
            for roll in possible_rolls:
                all_boards = self.generate_all_boards(board, roll)
                for new_board, _ in all_boards:
                    eval = self.minimax(new_board, depth - 1, False)
                    max_eval = max(max_eval, eval)
            return max_eval
        else:
            min_eval = float('inf')
            possible_rolls = self.get_possible_rolls()
            for roll in possible_rolls:
                all_boards = self.generate_all_boards(board, roll)
                for new_board, _ in all_boards:
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
            for j in range(i, 7):  # Start from i to avoid duplicates like (1, 6) and (6, 1)
                rolls.add((i, j))
        return list(rolls)
    
    def evaluate_moves(self, all_boards, roll):
        best_score = float('-inf') if self.color == "white" else float('inf')
        best_move = None

        for new_board, move_sequence in all_boards:
            score = evaluate_position(new_board, self.ratios)
            if (self.color == "white" and score > best_score) or (self.color == "black" and score < best_score):
                best_score = score
                best_move = move_sequence

        return best_move, best_score


    def generate_all_boards(self, board: list, roll: list):
        all_boards = []
        # When not all dice are the same, generate permutations
        if len(set(roll)) > 1:
            from itertools import permutations
            unique_permutations = set(permutations(roll))
            for permuted_roll in unique_permutations:
                self.generate_boards_recursive(board, list(permuted_roll), all_boards, [])
        else:
            # For doubles, no need for permutations
            self.generate_boards_recursive(board, roll, all_boards, [])
        return all_boards


    def generate_boards_recursive(self, board: list, roll: list, all_boards: list, move_sequence: list):
        if not roll:
            # Base case: no more dice rolls
            all_boards.append((copy.deepcopy(board), move_sequence))
            return

        # Use the first die in the roll list
        roll_value = roll[0]
        remaining_rolls = roll[1:]

        valid_moves = self.generate_moves(roll_value, board)

        if valid_moves:
            for move in valid_moves:
                # Simulate the move on a copied board
                new_board = self.simulate_move(copy.deepcopy(board), move)
                # Recursively generate boards for the remaining dice
                self.generate_boards_recursive(new_board, remaining_rolls, all_boards, move_sequence + [move])
        else:
            # No valid moves for this die, proceed to next die
            self.generate_boards_recursive(board, remaining_rolls, all_boards, move_sequence)

    def generate_moves(self, roll_value: int, board: list) -> list:
        moves = []
        captured_position = 26 if self.color == "white" else 27
        home_positions = range(19, 25) if self.color == "white" else range(1, 7)
        direction = 1 if self.color == "white" else -1

        # Check for captured pieces
        if board[captured_position] > 0:
            start_positions = [0 if self.color == "white" else 25]
        else:
            # Include only positions where the player has pieces, derived from the board
            start_positions = []
            for i in range(24):
                position = i + 1  # Positions 1 to 24
                checker_count = board[i]
                if self.color == "white" and checker_count > 0:
                    start_positions.append(position)
                elif self.color == "black" and checker_count < 0:
                    start_positions.append(position)

        for start in start_positions:
            target = start + direction * roll_value

            # Bearing off
            if (self.color == "white" and target > 24) or (self.color == "black" and target < 1):
                # Collect all player's positions from the board
                player_positions = []
                for i in range(24):
                    position = i + 1
                    checker_count = board[i]
                    if self.color == "white" and checker_count > 0:
                        player_positions.extend([position] * checker_count)
                    elif self.color == "black" and checker_count < 0:
                        player_positions.extend([position] * abs(checker_count))
                # Check if all pieces are in the home board
                if all(pos in home_positions for pos in player_positions):
                    target = 25 if self.color == "white" else 0
                    if self.valid_move_with_board(start, target, [str(roll_value)], board):
                        moves.append((start, target))
                continue

            if 1 <= target <= 24:
                if self.valid_move_with_board(start, target, [str(roll_value)], board):
                    moves.append((start, target))

        return moves
    
    def simulate_move(self, board: list, move: tuple) -> list:
        start, end = move
        new_board = copy.deepcopy(board)

        if self.color == "white":
            if start == 0:
                # Move a captured piece from the bar
                new_board[26] -= 1
            else:
                new_board[start - 1] -= 1

            if end == 25:
                # Bear off the piece
                new_board[24] += 1
            else:
                # Handle capturing opponent's piece
                if new_board[end - 1] < 0:
                    new_board[end - 1] = 1
                    new_board[27] += 1  # Black's captured pieces
                else:
                    new_board[end - 1] += 1
        else:
            if start == 25:
                # Move a captured piece from the bar
                new_board[27] -= 1
            else:
                new_board[start - 1] += 1

            if end == 0:
                # Bear off the piece
                new_board[25] += 1
            else:
                # Handle capturing opponent's piece
                if new_board[end - 1] > 0:
                    new_board[end - 1] = -1
                    new_board[26] += 1  # White's captured pieces
                else:
                    new_board[end - 1] -= 1

        return new_board