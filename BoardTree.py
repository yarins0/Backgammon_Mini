class BoardNode:
    def __init__(self, board, evaluation, path, player_turn):
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

    def add_child(self, child_node):
        """
        Add a child node to the current node.
        
        :param child_node: The child node to be added.
        """
        self.children.append(child_node)

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

    def update_root(self, new_root):
        self.root = new_root


# Example usage
if __name__ == "__main__":
    # Initialize the tree with a root board and its evaluation
    initial_board = "Initial Board State"
    initial_evaluation = 0
    tree = BoardTree(initial_board, initial_evaluation)

    # Add some boards to the tree
    node1 = tree.add_board(tree.root, "Board State 1", 10, "Move 1")
    node2 = tree.add_board(tree.root, "Board State 2", 20, "Move 2")
    tree.add_board(node1, "Board State 1.1", 15, "Move 1.1")
    tree.add_board(node2, "Board State 2.1", 25, "Move 2.1")

    # Traverse and print the tree
    tree.traverse()