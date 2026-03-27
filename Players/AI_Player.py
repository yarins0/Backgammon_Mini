from Players.Player import *
from Constants import *
import copy

class AI_Player(Player):
    def __init__(self, color: str = WHITE, board= START_BOARD):
        """
        AI Player that extends the base Player class with various decision-making
        strategies (heuristic, MCTS, neural, etc.).

        :param color: 'white' or 'black'
        :param board: The starting board state
        """
        super().__init__(color, board, is_human= False)
        

    def __str__(self) -> str:
        return f"AI Player ({self.color})"


