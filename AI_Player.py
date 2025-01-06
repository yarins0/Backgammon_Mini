from Player import Player
from BoardTree import BoardTree, BoardNode
from Constants import *
from Eval_position import evaluate_position
import copy

class AI_Player(Player):
    def __init__(self, color: str, board, ratios= EVAL_DISTRIBUTION):
        super().__init__(color, board, is_human= False)
        self.ratios = ratios
        # Initialize the board tree with the current board state
        self.board_tree = BoardTree(copy.deepcopy(self.board), evaluate_position(self.board, self.ratios))



    def play(self, roll: list) -> list:
        """
        Decides which move to make based on CHOSEN_EVAL_METHOD.
        Signature remains unchanged. 
        board_tree.reset_tree is used instead of manual re-initialization.
        """
        #self.pieces, self.other_pieces = self.convert_board_to_pieces_array(self.board)

        if CHOSEN_EVAL_METHOD == 1:
            return self.heuristic_play(roll)
        elif CHOSEN_EVAL_METHOD == 2:
            # Reset the tree in preparation for MCTS
            self.board_tree.reset_tree(
                self.board,
                evaluate_position(self.board, self.ratios),
                self.color
            )
            # Run MCTS to pick a move
            return self.mcts_play(roll)
        else:
            # Strategic (minimax) approach
            self.board_tree.reset_tree(
                self.board,
                evaluate_position(self.board, self.ratios),
                self.color
            )
            self.ensure_tree_depth(self.board_tree.root, MIN_MAX_DEPTH, current_roll=roll)
            return self.strategic_play(roll, depth=MIN_MAX_DEPTH)
        
        #for turnaments in anni platform:
        if executed_moves:
                for move in executed_moves:
                    # Execute each move
                    from_pos, to_pos = move
                    self.move_piece(from_pos, to_pos, roll)
    
        self.pieces, self.other_pieces = self.convert_board_to_pieces_array(self.board)

    def mcts_play(self, roll: list) -> list:
        """
        Executes a move using an MCTS-based approach. 
        Typically consists of multiple iterations of:
          1) Selection
          2) Expansion
          3) Simulation
          4) Backpropagation
        Finally, selects the best child of the root.
        """
        # Number of iterations; may be tuned
        MCTS_ITERATIONS = 128

        for _ in range(MCTS_ITERATIONS):
            self.mcts_iteration(self.board_tree.root, roll)

        # Pick the best move from children of root, e.g., highest evaluation
        best_move = None
        best_score = float('-inf') if self.color == "white" else float('inf')
        for child in self.board_tree.root.children:
            node_score = child.evaluation
            if (self.color == "white" and node_score > best_score) or \
               (self.color == "black" and node_score < best_score):
                best_score = node_score
                best_move = child.path

        if best_move:
            print(f"MCTS AI ({self.color}) executed moves: {best_move} with score: {best_score}")
            return best_move
        else:
            print("No valid moves found by MCTS.")
            return []

    def mcts_iteration(self, node: BoardNode, roll: list):
        """
        One iteration of MCTS:
          1) Selection
          2) Expansion
          3) Simulation
          4) Backpropagation
        """
        selected_node = self.mcts_select(node)
        expanded_node = self.mcts_expand(selected_node, roll)
        simulation_result = self.mcts_simulate(expanded_node)
        self.mcts_backpropagate(expanded_node, simulation_result)

    def mcts_select(self, node: BoardNode) -> BoardNode:
        """
        Navigate down the tree (e.g. using UCB) until we reach a node that can be expanded
        or is a terminal state.
        """
        return node  # Placeholder for your actual selection logic

    def mcts_expand(self, node: BoardNode, roll: list) -> BoardNode:
        """
        If not terminal and there's an unexpanded move, add one child node; otherwise,
        return node as is.
        """
        return node  # Placeholder for your actual expansion logic

    def mcts_simulate(self, node: BoardNode) -> float:
        """
        Simulate a playout from the node (e.g. random or heuristic-based) until terminal,
        and return a final value [0..1] indicating result from White’s perspective.
        """
        return evaluate_position(node.board, self.ratios)

    def mcts_backpropagate(self, node: BoardNode, result: float):
        """
        Traverse back up from node to root, updating visitation counts and accumulated
        values for each ancestor.
        """
        pass  # Placeholder for your actual backpropagation logic

    def heuristic_play(self, roll: list) -> list:
        all_moves = self.generate_all_moves(self.board, roll, current_color=self.color)
        best_move, best_score = self.evaluate_moves(all_moves)

        if best_move:
            print(f"AI ({self.color}) executed moves: {best_move} with score: {best_score}")
            return best_move
        else:
            print("No valid moves available for AI.")
            return []

    def strategic_play(self) -> list:
        best_score = float('-inf') if self.color == "white" else float('inf')
        best_move = None

        current_node = self.board_tree.root
        for child in current_node.children:
            if not child.path:
                continue
            last_moves = child.path[-1]
            if not last_moves:
                continue

            if (self.color == "white" and child.evaluation > best_score) \
               or (self.color == "black" and child.evaluation < best_score):
                best_score = child.evaluation
                best_move = last_moves

        if best_move:
            print(f"Strategic AI ({self.color}) executed moves: {best_move} with score: {best_score}")
            return best_move
        else:
            print("No valid moves available for Strategic AI.")
            return []

    def gen_minmax_tree(self, node: BoardNode, depth: int, current_roll=None):
        if depth == 0:
            node.evaluation = evaluate_position(node.board, self.ratios)
            return node.evaluation

        if current_roll is not None:
            rolls_to_use = [current_roll]
        else:
            rolls_to_use = self.get_possible_rolls()

        next_player_turn = "black" if node.player_turn == "white" else "white"

        for roll in rolls_to_use:
            all_moves = self.generate_all_moves(node.board, roll, current_color=node.player_turn)
            if not all_moves:
                new_node = BoardNode(
                    node.board,
                    evaluate_position(node.board, self.ratios),
                    node.path + [],
                    next_player_turn
                )
                node.add_child(new_node)
                self.gen_minmax_tree(new_node, depth - 1, None)
            else:
                for moves in all_moves:
                    child_board = copy.deepcopy(node.board)
                    self.simulate_moves(child_board, moves, current_color=node.player_turn)

                    child_node = BoardNode(
                        board=child_board,
                        evaluation=0.0,
                        path=node.path + [moves],
                        player_turn=next_player_turn
                    )
                    node.add_child(child_node)

                    self.gen_minmax_tree(child_node, depth - 1, None)

        if node.children:
            total = sum(child.evaluation for child in node.children)
            node.evaluation = total / len(node.children)

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
            new_board = self.simulate_moves(copy.deepcopy(self.board), moves, current_color=self.color)
            score = evaluate_position(new_board, self.ratios)
            if (self.color == "white" and score > best_score) or (self.color == "black" and score < best_score):
                best_score = score
                best_move = moves

        return best_move, best_score

    def generate_all_moves(self, board: list, roll: list, current_color=None) -> list:
        if current_color is None:
            current_color = self.color
        all_moves = []
        self.generate_moves_recursive(board, roll, [], all_moves, current_color)
        return all_moves

    def generate_moves_recursive(self, board: list, rolls: list, move_sequence: list, all_moves: list, current_color: str):
        if not rolls:
            all_moves.append(move_sequence)
            return

        captured_pos = self.get_captured_position(current_color)
        pieces_on_bar = board[captured_pos]
        possible_moves_found = False

        sorted_rolls = sorted(rolls, reverse=True)
        unique_rolls = set(sorted_rolls)

        for roll_val in unique_rolls:
            remaining_rolls = sorted_rolls.copy()
            remaining_rolls.remove(roll_val)
            possible_moves = self.generate_valid_moves([roll_val], board, current_color)

            if pieces_on_bar > 0:
                possible_moves = [m for m in possible_moves if m[0] == captured_pos]

            if not possible_moves:
                continue

            possible_moves_found = True
            for move in possible_moves:
                new_board = self.simulate_move(copy.deepcopy(board), move, current_color)
                self.generate_moves_recursive(
                    new_board,
                    remaining_rolls,
                    move_sequence + [move],
                    all_moves,
                    current_color
                )

        if not possible_moves_found:
            all_moves.append(move_sequence)

    def generate_valid_moves(self, roll_values: list, board: list, current_color: str) -> list:
        moves = []
        captured_position = self.get_captured_position(current_color)

        if self.captured_piece_on_board(board, current_color):
            from_positions = [captured_position]
        else:
            from_positions = [
                i for i in range(24)
                if self.is_piece_at_position_on_board(i, board, current_color)
            ]

        for from_pos in from_positions:
            for die in roll_values:
                to_pos = self.calculate_target_position(from_pos, die, current_color)
                if self.valid_move_with_board(from_pos, to_pos, [die], board, current_color):
                    moves.append((from_pos, to_pos))
        return moves

    def simulate_moves(self, board: list, moves: list, current_color=None) -> list:
        if current_color is None:
            current_color = self.color
        for move in moves:
            self.simulate_move(board, move, current_color)
        return board

    def simulate_move(self, board: list, move: tuple, current_color=None) -> list:
        if current_color is None:
            current_color = self.color
        from_pos, to_pos = move

        if self.is_piece_at_position_on_board(from_pos, board, current_color):
            self.remove_piece_from_board(board, from_pos, current_color)
        else:
            print(f"No piece at position {from_pos} to move for {current_color}")
            return board

        if self.is_opponent_piece_at_position_on_board(to_pos, board, current_color):
            self.capture_opponent_piece(board, to_pos, current_color)

        self.add_piece_to_board(board, to_pos, current_color)
        return board

    def valid_move_with_board(self, from_pos, to_pos, roll_values, board, current_color) -> bool:
        # Validate the move based on the board state
        if self.is_blocked_on_board(to_pos, board, current_color):
            return False
        if not self.is_piece_at_position_on_board(from_pos, board, current_color):
            return False
        
        roll_values = [int(value) for value in roll_values]

        if from_pos == self.get_captured_position(current_color):
            move_distance = None
            for die_value in roll_values:
                expected_to_pos = die_value - 1 if current_color == "white" else 24 - die_value
                if expected_to_pos == to_pos:
                    move_distance = die_value
                    break
            if move_distance is None:
                return False
            
        elif to_pos == self.get_escaped_position(current_color):
            if not self.all_pieces_in_home_board(board, current_color):
                return False
            if not self.can_bear_off_from_position(from_pos, board, current_color):
                return False
            if not any(die >= from_pos + 1 for die in roll_values) and current_color == "black":
                return False
            if not any(die >= 24 - from_pos for die in roll_values) and current_color == "white":
                return False
            
        else:
            move_distance = to_pos - from_pos if current_color == "white" else from_pos - to_pos

            if move_distance <= 0:
                return False
            
        return True

    def can_bear_off_from_position(self, position, board, current_color):
        if current_color == "white":
            for pos in range(18, position):
                if board[pos] > 0:
                    return False
        else:
            for pos in range(5, position, -1):
                if board[pos] < 0:
                    return False
        return True

    def is_blocked_on_board(self, position, board, current_color):
        if position < 0 or position > 23:
            return False
        occupant_count = board[position]
        # Determine the opponent color
        opp_color = "white" if current_color == "black" else "black"
        if opp_color == "white":
            return occupant_count >= 2
        else:
            return occupant_count <= -2

    def all_pieces_in_home_board(self, board, current_color):
        if current_color == "white":
            for pos in range(24):
                if board[pos] > 0 and pos < 18:
                    return False
        else:
            for pos in range(24):
                if board[pos] < 0 and pos > 5:
                    return False
        return True

    def is_opponent_piece_at_position_on_board(self, position, board, current_color):
        if position < 0 or position > 23:
            return False
        occupant_count = board[position]
        opp_color = "white" if current_color == "black" else "black"
        if opp_color == "white":
            return occupant_count > 0
        else:
            return occupant_count < 0

    def capture_opponent_piece(self, board, position, current_color):
        opp_color = "white" if current_color == "black" else "black"
        self.remove_piece_from_board(board, position, opp_color)
        board[self.get_captured_position(opp_color)] += 1

    def add_piece_to_board(self, board, position, current_color):
        if 0 <= position <= 23:
            if current_color == "white":
                board[position] += 1
            else:
                board[position] -= 1
        else:
            board[position] += 1  # bearing off or captured

    def remove_piece_from_board(self, board, position, current_color):
        if 0 <= position <= 23:
            if current_color == "white":
                board[position] -= 1
            else:
                board[position] += 1
        else:
            board[position] -= 1  # bearing off or captured

    def captured_piece_on_board(self, board, color):
        return board[self.get_captured_position(color)] > 0

    def is_piece_at_position_on_board(self, position, board, color = None):
        if color is None:
            color = self.color

        if position < 0 or position > 23:
            return board[position] > 0
        else:
            return board[position] > 0 if color == "white" else board[position] < 0

    def win_on_board(self, board, color=None):
        if color is None:
            color = self.color

        return board[self.get_escaped_position(color)] == 15