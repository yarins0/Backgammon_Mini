import random
import time
from HeuristicNet import neural_eval
from Player import *
from BoardTree import BoardTree, BoardNode
from Constants import *
from Eval_position import evaluate_position
import copy

class AI_Player(Player):
    def __init__(self, color: str = WHITE, board= START_BOARD, ratios= EVAL_DISTRIBUTION, model_path=PATH):
        """
        AI Player that extends the base Player class with various decision-making
        strategies (heuristic, MCTS, neural, etc.).

        :param color: 'white' or 'black'
        :param board: The starting board state
        :param ratios: Weights for heuristic evaluation
        :param model_path: Path to a trained model (if using neural_eval)
        """
        super().__init__(color, board, is_human= False)
        
        self.ratios = ratios
        self.model_path = model_path

        # Initialize the board tree with the current board state
        self.board_tree = BoardTree(copy.deepcopy(self.board), evaluate_position(self.board, self.ratios))

    def __str__(self) -> str:
        return f"AI Player ({self.color})"

    def choose_move(self, board:list ,roll: list, current_color=None, time = AI_TURN_TIME) -> list:
        """
        Main entry point for the AI to decide which move to make, based on CHOSEN_EVAL_METHOD.

        :param board: Current board state
        :param roll: Dice roll (list of dice)
        :param current_color: Whose turn it is. Defaults to self.color
        :param time: Time limit for AI moves (used by MCTS)
        :return: List of (from_pos, to_pos) moves decided by AI
        """
        #self.pieces, self.other_pieces = self.convert_board_to_pieces_array(self.board)
        self.board = board
        if current_color is None:
            current_color = self.color

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
            return self.mcts_play(roll, time)
        
        elif CHOSEN_EVAL_METHOD == 3:
            # Strategic (minimax) approach
            self.board_tree.reset_tree(
                copy.deepcopy(self.board),
                evaluate_position(self.board, self.ratios),
                self.color
            )
            self.generate_minmax_tree(self.board_tree.root, MIN_MAX_DEPTH, current_roll=roll)
            return self.strategic_play()
        elif CHOSEN_EVAL_METHOD == 4:
            return self.neural_play(roll)  # Default to neural evaluation
        else:
            return self.random_play(roll) # Default to random play
        
        #for turnaments in anni platform:
        #if executed_moves:
        #       for move in executed_moves:
        #          # Execute each move
        #         from_pos, to_pos = move
        #        self.move_piece(from_pos, to_pos, roll)
    
        #self.pieces, self.other_pieces = self.convert_board_to_pieces_array(self.board)

    def neural_play(self, roll: list) -> list:
        """
        Use a trained neural network to evaluate all possible moves and pick the best move.

        :param roll: Dice roll
        :return: Best move as a list of (from_pos, to_pos)
        """
        all_moves = self.generate_all_moves(self.board, roll, current_color=self.color)
        best_move, best_score = self.choose_neural_best_move(all_moves)

        if best_move:
            if DEBUG_MODE:
                print(f"Neural AI ({self.model_path})-{self.color} executed moves: {best_move} with score: {best_score}")
            return best_move
        else:
            if DEBUG_MODE:
                print("No valid moves available for Neural AI.")
            return []
        
    def choose_neural_best_move(self, all_moves):
        best_score = float('-inf')
        best_move = None

        for moves in all_moves:
            new_board = self.simulate_moves(copy.deepcopy(self.board), moves, current_color=self.color)
            score = neural_eval(new_board, self.color , self.model_path)
            if score == 1.0: #best possible score
                return moves, score
            if score > best_score:
                best_score = score
                best_move = moves
        return best_move, best_score
    
    def mcts_play(self, roll: list, time = AI_TURN_TIME) -> list:
        """
        Executes a move using an MCTS-based approach. 
        Typically consists of multiple iterations of:
          1) Selection
          2) Expansion
          3) Simulation
          4) Backpropagation
        
        :param roll: Dice roll
        :param time: Time limit for MCTS
        :return: Best move as a list of (from_pos, to_pos)
        """
        
        # Pick the best move from children of root, e.g., highest evaluation
        best_child = self.UCT_search(self.board_tree.root, roll, time)  

        best_move = None
        if best_child:
            best_move = best_child.get_last_move()

        if best_move:
            if DEBUG_MODE:
                print(f"MCTS AI ({self.color}) executed moves: {best_move} with score: {best_child.wins}")
            return best_move
        else: 
            if DEBUG_MODE:
                print("No valid moves available for AI.")
            return []
            
    def UCT_search(self, node: BoardNode, roll: list, time_lim = AI_TURN_TIME):
        """
        Run multiple MCTS iterations until time is up, then pick the best child of the root.

        :param node: Root node of the MCTS tree
        :param roll: Dice roll for the first expansion (optional)
        :param time_lim: Time limit in seconds
        :return: The best child node based on UCB
        """

        end_time = time.time() + time_lim
        sent_roll = copy.deepcopy(roll)

        while time.time() < end_time:
            self.mcts_select(node, sent_roll)
            sent_roll = None

        return node.get_best_ucb_child()

    def mcts_select(self, node: BoardNode, roll: list = None)-> BoardNode:
        """
        Descend the tree using UCB until we find a node to expand or we reach a terminal node.

        :param node: Current node
        :param roll: Dice roll for expansion (may be None)
        :return: The node we ended on
        """
        current_node = node
        
        while current_node is not None and not current_node.is_terminal():
            gen_all = True
            if roll is None:
                gen_all = False
                roll = self.get_random_roll()

            # If the node is not fully expanded, expand it
            if not current_node.is_fully_expanded(roll):
                if gen_all:
                    child_node = self.mcts_expand_all_moves(current_node, roll)
                else:
                    child_node = self.mcts_expand(current_node, roll)

                # If expand() returns None, it means no new child could be created
                # (often due to no legal moves). Stop selection.
                if child_node is None:
                    break
                
                return child_node
            
            # Otherwise, if the node is fully expanded, we pick a child to explore
            else:
                next_node = current_node.get_best_ucb_child(MCTS_C, 1 if current_node.player_turn == self.color else -1)
                
                # If we can't pick a valid child, stop
                if next_node is None:
                    break
                
                current_node = next_node

        # Once the loop is done, return whatever node we ended on
        return current_node
    
    def mcts_expand_all_moves(self, node, roll):
        """
        Expand by generating all possible child states from the current node.

        :param node: Current node
        :param roll: Dice roll
        :return: The child node with the best UCB, or node if no expansions
        """
        if node.is_fully_expanded(roll):
            return node
        
        all_moves = self.generate_all_moves(node.board, roll, current_color=node.player_turn)
        if not all_moves:
            return node # No valid moves available

        for move in all_moves:
            new_board = self.simulate_moves(copy.deepcopy(node.board), move, current_color=node.player_turn)
            new_node = BoardNode(
                new_board,
                0.0,
                node.path + [move],
                self.get_next_player(node.player_turn)
            )
            node.add_child(new_node)
            self.mcts_backpropagate(new_node, self.mcts_simulate(new_node))

        # Mark this node as fully expanded now that we added all moves.
        node.fully_expand_roll(roll)

        return node.get_best_ucb_child(MCTS_C, 1 if node.player_turn == self.color else -1)
                
    def mcts_expand(self, node: BoardNode, roll: list, ) -> BoardNode:
        """
        If not terminal and there's an unexpanded move, add one child node; otherwise,
        return node as is.
        """

        if node.is_fully_expanded(roll):
            return node
        
        all_moves = self.generate_all_moves(node.board, roll, current_color=node.player_turn)
        if not all_moves:
            return node # No valid moves available
        
        #get the last moves of the children
        last_moves = [child.get_last_move() for child in node.children]

        for move in all_moves:
            if move not in last_moves:
                new_board = self.simulate_moves(copy.deepcopy(node.board), move, current_color=node.player_turn)
                new_node = BoardNode(
                    new_board,
                    0.0,
                    node.path + [move],
                    self.get_next_player(node.player_turn)
                )
                node.add_child(new_node)
                print(f"new node: moves:{new_node.path}")
                self.mcts_backpropagate(new_node, self.mcts_simulate(new_node))
                return new_node
                
        # Mark this node as fully expanded now that we added all moves.
        node.fully_expand_roll(roll)
        return node

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
        while node is not None:
            node.visits += 1
            node.wins += result
            node = node.parent

    def random_play(self, roll: list) -> list:
        all_moves = self.generate_all_moves(self.board, roll, current_color=self.color)
        rnd_indx = random.randint(0, len(all_moves) - 1) if all_moves else 0
        return all_moves[rnd_indx] if all_moves else []
     
    def heuristic_play(self, roll: list) -> list:
        '''
        Get the best move best on possible boards heuristic evaluation.
        '''
        all_moves = self.generate_all_moves(self.board, roll, current_color=self.color)
        best_move, best_score = self.choose_heuristic_best_move(all_moves)

        if best_move:
            if DEBUG_MODE:
                print(f"AI ({self.color}) executed moves: {best_move} with score: {best_score}")
            return best_move
        else:
            if DEBUG_MODE:
                print("No valid moves available for AI.")
            return []
        
    def choose_heuristic_best_move(self, all_moves, moves_size=1):
        best_score = float('-inf') if self.color == WHITE else float('inf')
        best_move = None
        color_param = 1 if self.color == WHITE else -1

        for moves in all_moves:
            new_board = self.simulate_moves(copy.deepcopy(self.board), moves, current_color=self.color)
            score = evaluate_position(new_board, self.ratios)
            if color_param * score > color_param * best_score:
                best_score = score
                best_move = moves

        return best_move, best_score
    
    def choose_heuristic_top_moves(self, all_moves, top_x=1):
        """
        Returns the top X moves (along with their scores) based on a heuristic evaluation.
        Sorts moves in descending order for WHITE, ascending for BLACK.

        :param all_moves: All possible move sequences
        :param top_x: How many moves to return in the sorted list
        :return: A list of tuples [(move_sequence, score), ...] of size up to top_x
        """
        scored_moves = []
        for move_seq in all_moves:
            new_board = self.simulate_moves(copy.deepcopy(self.board), move_seq, current_color=self.color)
            score = evaluate_position(new_board, self.ratios)
            scored_moves.append((move_seq, score))

        # If White, we sort descending by score. If Black, ascending.
        if self.color == WHITE:
            scored_moves.sort(key=lambda x: x[1], reverse=True)
        else:
            scored_moves.sort(key=lambda x: x[1])

        # Return up to top_x best
        return scored_moves[:top_x]

    def strategic_play(self) -> list:
        current_node = self.board_tree.root
        best_child = current_node.get_best_evaluation_child()

        if best_child:
            best_move = best_child.get_last_move()

        if best_move:
            print(f"Strategic AI ({self.color}) executed moves: {best_move} with score: {best_child.get_evaluation()}")
            return best_move
        else:
            print("No valid moves available for Strategic AI.")
            return []

    def generate_minmax_tree(self, node: BoardNode, depth: int, current_roll=None):
        if depth == 0:
            node.evaluation = evaluate_position(node.board, self.ratios)
            return node.evaluation
        
        if current_roll is not None:
            rolls_to_use = [current_roll]
        else:
            rolls_to_use = self.generate_all_possible_rolls()

        next_player_turn = self.get_next_player(node.player_turn)

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
                self.generate_minmax_tree(new_node, depth - 1, None)
            else:
                for moves in all_moves:
                    child_board = copy.deepcopy(node.board)
                    self.simulate_moves(child_board, moves, current_color=node.player_turn)

                    child_node = BoardNode(
                        board= child_board,
                        evaluation= 0.0,
                        path= node.path + [moves],
                        player_turn= next_player_turn
                    )
                    node.add_child(child_node)

                    self.generate_minmax_tree(child_node, depth - 1, None)

        if node.children:
            total = sum(child.evaluation for child in node.children)
            node.evaluation = total / len(node.children)

    def get_random_roll(self) -> list:
        i = random.randint(1, 6)
        j = random.randint(1, 6)
        if i == j:
            return [i, i, i, i]
        else:
            return [i, j]
        
    def generate_all_possible_rolls(self) -> list:
        """
        Generate all unique dice roll combinations.
        :return: A list of unique dice roll combinations.
        """
        rolls = set()
        for i in range(1, 7):
            for j in range(i, 7):
                if i == j:
                    rolls.add((i, i, i, i))  # Doubles are played four times
                else:
                    rolls.add((i, j))
        return list(rolls)

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

        captured_pos = get_captured_position(current_color)
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
        if self.has_captured_piece(board, current_color):
            from_positions = [get_captured_position(current_color)]
        else:
            from_positions = [
                i for i in range(24)
                if self.is_piece_at_position(i, board, current_color)
            ]

        moves = []
        for from_pos in from_positions:
            for die in roll_values:
                to_pos = self.calculate_target_position(from_pos, die, current_color)
                if self.valid_move(from_pos, to_pos, die , board, current_color, simulate=True):
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

        #remove the piece from the starting position
        if self.is_piece_at_position(from_pos, board, current_color):
            self.remove_piece(from_pos, board, current_color)
        else:
            print(f"No piece at position {from_pos} to move for {current_color}")
            return board

        #capture opponent piece if necessary
        self.capture_piece_at_position(to_pos, board, current_color, simulate = True)

        #add the piece to the target position
        self.add_piece(to_pos, board, current_color)
        return board
