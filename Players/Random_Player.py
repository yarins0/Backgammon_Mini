import random
from Constants import *
from Players.AI_Player import AI_Player
class Random_Player(AI_Player):
    def __init__(self, color: str = WHITE, board= START_BOARD):
        """
        AI Player that extends the base Player class with various decision-making
        strategies (heuristic, MCTS, neural, etc.).

        :param color: 'white' or 'black'
        :param board: The starting board state
        :param ratios: Weights for heuristic evaluation
        :param model_path: Path to a trained model (if using neural_eval)
        """
        super().__init__(color, board)
        

    def __str__(self) -> str:
        return f"Random Player ({self.color})"

    def choose_move(self, board:list ,roll: list, current_color=None) -> list:
        """
        Chooses a random move from the list of all possible moves.
        :param board: The current board state
        :param roll: The current dice roll
        :return: A move to make
        """
        self.board = board
        if current_color is None:
            current_color = self.color

        all_moves = self.generate_all_moves(self.board, roll, current_color=self.color)
        rnd_indx = random.randint(0, len(all_moves) - 1) if all_moves else 0
        if all_moves:
            if DEBUG_MODE:
                print(f"{self} executed moves: {all_moves[rnd_indx]}.")
            return all_moves[rnd_indx]
        else:
            if DEBUG_MODE:
                print("No valid moves available for Neural AI.")
            return []
             