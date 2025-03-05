
import random
import time
import copy
from Constants import *
from Players.AI_Player import AI_Player
from Eval_position import evaluate_position
from BoardTree import *

class MCTS_Player(AI_Player):
    def __init__(self, color: str = WHITE, board= START_BOARD, ratios= EVAL_DISTRIBUTION, c= MCTS_C):
        """
        AI Player that extends the base Player class with various decision-making
        strategies (heuristic, MCTS, neural, etc.).

        :param color: 'white' or 'black'
        :param board: The starting board state
        :param ratios: Weights for heuristic evaluation
        :param model_path: Path to a trained model (if using neural_eval)
        """
        super().__init__(color, board)
        
        self.ratios = ratios
        self.c = c
        
        # Initialize the board tree with the current board state
        self.board_tree = BoardTree(copy.deepcopy(self.board), evaluate_position(self.board, self.ratios))

    def __str__(self) -> str:
        return f"MCTS AI ({self.color})"

    def choose_move(self, board:list ,roll: list, current_color=None, time = AI_TURN_TIME) -> list:
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
        
        #self.pieces, self.other_pieces = self.convert_board_to_pieces_array(self.board)
        self.board = board
        if current_color is None:
            current_color = self.color

    
        # Reset the tree in preparation for MCTS
        self.board_tree.reset_tree(
            self.board,
            evaluate_position(self.board, self.ratios),
            self.color
        )
        
        # Run MCTS to pick a move

        # Pick the best move from children of root, e.g., highest evaluation
        best_child = self.UCT_search(self.board_tree.root, roll, time)  

        best_move = None
        if best_child:
            best_move = best_child.get_last_move()

        if best_move:
            if DEBUG_MODE:
                print(f"{self} executed moves: {best_move} with score: {best_child.wins}")
            return best_move
        else: 
            if DEBUG_MODE:
                print(f"No valid moves available for {self}.")
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
                next_node = current_node.get_best_ucb_child(self.c, 1 if current_node.player_turn == self.color else -1)
                
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

        return node.get_best_ucb_child(self.c, 1 if node.player_turn == self.color else -1)
                
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
    
    def get_random_roll(self) -> list:
        i = random.randint(1, 6)
        j = random.randint(1, 6)
        if i == j:
            return [i, i, i, i]
        else:
            return [i, j]
        