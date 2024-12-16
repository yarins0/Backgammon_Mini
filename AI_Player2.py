from Player import *
from BoardTree import *
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

    def update_board_tree(self, move_sequence: list):
        """
        Update the board tree by setting the root to the node reached by the move sequence.
        If the node is not found and the move sequence is legal, regenerate the tree from the current board state.
        
        :param move_sequence: A list of moves representing the path to the new root.
        """
        current_node = self.board_tree.root
        for move in move_sequence:
            # Find the child node that matches the move
            for child in current_node.children:
                if child.path[-1] == move:
                    current_node = child
                    break
            else:
                # Validate the move sequence on the updated board
                if self.is_legal_move_sequence(move_sequence):
                    # If the node is not found and the move is legal, regenerate the tree
                    print("Move sequence not found in the tree. Regenerating the tree.")
                    self.regenerate_tree_from_current_state()
                else:
                    print("Illegal move sequence. Tree regeneration aborted.")
                return
        
        # Update the root to the reached node
        self.board_tree.update_root(current_node)

    def is_legal_move_sequence(self, move_sequence: list) -> bool:
        """
        Check if the given move sequence is legal on the updated board state.
        
        :param move_sequence: A list of moves to validate.
        :return: True if the move sequence is legal, False otherwise.
        """
        # Create a copy of the current board state
        board_copy = self._pieces[:]
        for move in move_sequence:
            # Validate the structure of the move
            if not isinstance(move, (list, tuple)) or len(move) != 2:
                print(f"Invalid move structure: {move}")
                return False
            
            start, end = move
            if not self.valid_move(start, end, [abs(end - start)]):
                return False
            # Simulate the move on the board copy
            self.simulate_move(board_copy, move)
        return True

    def regenerate_tree_from_current_state(self):
        """
        Regenerate the board tree from the current board state and expand it to the required depth.
        """
        # Create a new root node with the current board state
        current_board_state = self._pieces[:]
        self.board_tree = BoardTree(current_board_state, evaluate_position(current_board_state, self.ratios))
        
        # Expand the tree to the required depth
        self.ensure_tree_depth(self.board_tree.root, MIN_MAX_DEPTH)

    def ensure_tree_depth(self, node: BoardNode, depth: int):
        if depth == 0:
            return

        # Get all possible dice rolls
        possible_rolls = self.get_possible_rolls()

        for roll in possible_rolls:
            # Generate all possible boards from the current node for each roll
            all_boards = self.generate_all_boards(node.board, roll)

            for new_board, move_sequence in all_boards:
                # Determine the next player's turn
                next_player_turn = "black" if node.player_turn == "white" else "white"

                # Check if the move sequence already exists in the children
                existing_child = next((child for child in node.children if child.path == move_sequence), None)
                if not existing_child:
                    # Add new child node if it doesn't exist
                    new_node = BoardNode(new_board, evaluate_position(new_board, self.ratios), move_sequence, next_player_turn)
                    node.add_child(new_node)
                    # Recursively ensure depth for the new child
                    self.ensure_tree_depth(new_node, depth - 1)

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
            # Separate moves that free captured pieces
            captured_moves = [move for move in best_move if (self.color == "white" and move[0] == 0) or (self.color == "black" and move[0] == 25)]
            other_moves = [move for move in best_move if move not in captured_moves]

            # Execute moves that free captured pieces first
            print(f"AI ({self.color}) executed moves: {captured_moves + other_moves} with score: {best_score}")
            return captured_moves + other_moves
        
        else:
            print("No valid moves available for AI.")
            return []  # Return an empty list instead of None


    def strategic_play(self, board: list, roll: list, depth: int = 2) -> list:
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
        if depth == 0 or self.win():
            return evaluate_position(node.board, self.ratios)

        if node.player_turn == "white":
            max_eval = float('-inf')
            for child in node.children:
                # Only decrement depth when switching to the opponent's turn
                eval = self.minimax(child, depth - 1 if child.player_turn == "black" else depth)
                max_eval = max(max_eval, eval)
            return max_eval
        else:
            min_eval = float('inf')
            for child in node.children:
                # Only decrement depth when switching to the opponent's turn
                eval = self.minimax(child, depth - 1 if child.player_turn == "white" else depth)
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