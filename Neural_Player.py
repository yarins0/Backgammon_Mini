from Constants import *
from AI_Player import AI_Player
from HeuristicNet import neural_eval
import copy

class Neural_Player(AI_Player):
    def __init__(self, color: str = WHITE, board= START_BOARD, model_path=PATH):
        """
        AI Player that extends the base Player class with various decision-making
        strategies (heuristic, MCTS, neural, etc.).

        :param color: 'white' or 'black'
        :param board: The starting board state
        :param ratios: Weights for heuristic evaluation
        """
        super().__init__(color, board)
        
        self.model_path = model_path

    def __str__(self) -> str:
        return f"Neural AI Player - {self.model_path} ({self.color})"


    def choose_move(self, board:list ,roll: list, current_color=None) -> list:
        """
        Use a trained neural network to evaluate all possible moves and pick the best move.

        :param roll: Dice roll
        :return: Best move as a list of (from_pos, to_pos)
        """
        self.board = board
        if current_color is None:
            current_color = self.color

        all_moves = self.generate_all_moves(self.board, roll, current_color=self.color)
        best_move, best_score = self.choose_neural_best_move(all_moves)

        if best_move:
            if DEBUG_MODE:
                print(f"{self} executed moves: {best_move} with score: {best_score}")
            return best_move
        else:
            if DEBUG_MODE:
                print(f"No valid moves available for {self}.")
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