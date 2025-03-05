from Constants import *
from Players.AI_Player import *
from Eval_position import evaluate_position
import copy

class Heuristic_Player(AI_Player):
    def __init__(self, color: str = WHITE, board= START_BOARD, ratios= EVAL_DISTRIBUTION):
        """
        AI Player that extends the base Player class with various decision-making
        strategies (heuristic, MCTS, neural, etc.).

        :param color: 'white' or 'black'
        :param board: The starting board state
        :param ratios: Weights for heuristic evaluation
        """
        super().__init__(color, board)
        
        self.ratios = ratios

    def __str__(self) -> str:
        return f"Heuristic Player ({self.color})"
    
    def print_ratios(self):
        print(f"Ratios: {self.ratios}")

    def choose_move(self, board:list ,roll: list, current_color=None, time = AI_TURN_TIME) -> list:
        '''
        Get the best move best on possible boards heuristic evaluation.
        '''
        self.board = board
        if current_color is None:
            current_color = self.color

        all_moves = self.generate_all_moves(self.board, roll, current_color=self.color)
        best_move, best_score = self.choose_heuristic_best_move(all_moves)

        if best_move:
            if DEBUG_MODE:
                print(f"{self} executed moves: {best_move} with score: {best_score}")
            return best_move
        else:
            if DEBUG_MODE:
                print(f"No valid moves available for {self}.")
            return []
        
    def choose_heuristic_best_move(self, all_moves):
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
