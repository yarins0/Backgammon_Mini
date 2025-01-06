import math
from Constants import MCTS_C, WHITE, BLACK


class BoardNode:
    def __init__(self, board, evaluation, path, player_turn, visits=0, wins=0, parent=None): 
        """
        Initialize a board node.
        
        :param board: The current board state.
        :param evaluation: The evaluation score of the board.
        :param path: The path taken to reach this board from the root.
        :param player_turn: The color of the player whose turn it is.
        """
        self.board = board
        self.evaluation = evaluation
        self.path = path
        self.player_turn = player_turn
        self.children = []
        self.visits = visits
        self.wins = wins
        self.parent = parent
        self.fully_expanded_rolls = []
        self.terminal = False

    def is_terminal(self):
        """
        Check if the game is won.
        """
        if self.terminal or self.board[24] == 15 or self.board[0] == 15:
            self.terminal = True
            
        return self.terminal
    
    def is_fully_expanded(self, roll):
        return set(roll) in self.fully_expanded_rolls
    
    def fully_expand_roll(self, roll):
        self.fully_expanded_rolls.append(set(roll))
    
    def get_evaluation(self):
        """
        Get the evaluation score of the board.
        """
        return self.evaluation
    
    def get_last_move(self):
        """
        Get the last move taken to reach the current board.
        """
        return self.path[-1] if self.path else None
    
    def add_child(self, child_node):
        """
        Add a child node to the current node.
        
        :param child_node: The child node to be added.
        """
        self.children.append(child_node)
        self.wins += child_node.wins
        child_node.parent = self

    def get_ucb(self, c=MCTS_C , direction = 1):
        """
        Calculate the Upper Confidence Bound (UCB) for the node.
        
        :param c: The exploration parameter.
        """
        if self.visits == 0:
            return float("inf")
        return direction * self.wins / self.visits + c * ((math.log(self.parent.visits) / self.visits) ** 0.5)
    
    def get_best_ucb_child(self, c= MCTS_C, direction = 1):
        """
        Get the child node with the highest UCB value.
        """
        best_child = None
        best_ucb = float("-inf")
        for child in self.children:
            ucb = child.get_ucb(c , direction)
            if ucb > best_ucb:
                best_ucb = ucb
                best_child = child
        return best_child
    
    def get_most_visited_child(self):
        """
        Get the child node with the highest number of visits.
        """
        best_child = None
        best_visits = 0
        for child in self.children:
            if child.visits > best_visits:
                best_visits = child.visits
                best_child = child
        return best_child
    
    def get_best_evaluation_child(self):
        """
        Get the child node with the highest evaluation score.
        """
        best_child = None
        best_evaluation = float("-inf") if self.player_turn == WHITE else float("inf")
        for child in self.children:
            if (child.evaluation > best_evaluation and self.player_turn == WHITE)\
                  or (child.evaluation < best_evaluation and self.player_turn == BLACK):
                best_evaluation = child.evaluation
                best_child = child
        return best_child
    

class BoardTree:
    def __init__(self, root_board, root_evaluation):
        """
        Initialize the board tree with a root node.
        
        :param root_board: The initial board state.
        :param root_evaluation: The evaluation score of the root board.
        """
        self.root = BoardNode(root_board, root_evaluation, path=[], player_turn="white")

    def add_board(self, current_node, new_board, evaluation, move, player_turn):
        """
        Add a new board to the tree.
        
        :param current_node: The node from which the new board is derived.
        :param new_board: The new board state.
        :param evaluation: The evaluation score of the new board.
        :param move: The move taken to reach the new board.
        :param player_turn: The color of the player whose turn it is.
        """
        new_path = current_node.path + [move]
        new_node = BoardNode(new_board, evaluation, new_path, player_turn)
        current_node.add_child(new_node)
        return new_node

    def traverse(self, node=None, depth=0):
        """
        Traverse the tree and print each node's board and evaluation.
        
        :param node: The current node to start traversal from.
        :param depth: The current depth of traversal.
        """
        if node is None:
            node = self.root
        
        print(f"Depth {depth}: Board: {node.board}, Evaluation: {node.evaluation}, Path: {node.path}")
        for child in node.children:
            self.traverse(child, depth + 1)

    def reset_tree(self , board, evaluation,  color):
        """
        Reset the tree by clearing all nodes except the root.
        """
        # Update the board tree root with the current board state
        self.root.board = board
        self.root.evaluation = evaluation
        self.root.path = []
        self.root.player_turn = color
        self.root.children = []  # Clear previous children
        
    def update_root(self, new_root):
        self.root = new_root

