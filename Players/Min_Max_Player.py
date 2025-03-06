from Constants import *
from Players.AI_Player import AI_Player
from Eval_position import evaluate_position
import copy
from BoardTree import *
class Min_Max_Player(AI_Player):
    def __init__(self, color: str = WHITE, board= START_BOARD, ratios= EVAL_DISTRIBUTION, depth= MIN_MAX_DEPTH):
        """
        AI Player that extends the base Player class with various decision-making
        strategies (heuristic, MCTS, neural, etc.).

        :param color: 'white' or 'black'
        :param board: The starting board state
        :param ratios: Weights for heuristic evaluation
        :param depth: The depth of the min-max tree
        """
        super().__init__(color, board)
        
        self.ratios = ratios
        self.depth = depth

        # Initialize the board tree with the current board state
        self.board_tree = BoardTree(copy.deepcopy(self.board), evaluate_position(self.board, self.ratios))

    def __str__(self) -> str:
        return f"Min Max AI Player ({self.color})"

    def choose_move(self, board:list ,roll: list, current_color=None) -> list:
        self.board = board
        if current_color is None:
            current_color = self.color

        self.board_tree.reset_tree(
            copy.deepcopy(self.board),
            evaluate_position(self.board, self.ratios),
            self.color
        )
        self.generate_minmax_tree(self.board_tree.root, self.depth, current_roll=roll)
        current_node = self.board_tree.root
        best_child = current_node.get_best_evaluation_child()

        if best_child:
            best_move = best_child.get_last_move()

        if best_move:
            if DEBUG_MODE:
                print(f"{self} executed moves: {best_move} with score: {best_child.get_evaluation()}")
            return best_move
        else:
            if DEBUG_MODE:
                print(f"No valid moves available for {self}.")
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