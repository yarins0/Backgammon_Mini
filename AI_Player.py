from Player import *
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

    def choose_move(self, board:list ,roll: list, current_color=None, time = AI_TURN_TIME) -> list:
        """
        Main entry point for the AI to decide which move to make, based on CHOSEN_EVAL_METHOD.

        :param board: Current board state
        :param roll: Dice roll (list of dice)
        :param current_color: Whose turn it is. Defaults to self.color
        :param time: Time limit for AI moves (used by MCTS)
        :return: List of (from_pos, to_pos) moves decided by AI
        """

        
        #for turnaments in anni platform:
        #if executed_moves:
        #       for move in executed_moves:
        #          # Execute each move
        #         from_pos, to_pos = move
        #        self.move_piece(from_pos, to_pos, roll)
    
        #self.pieces, self.other_pieces = self.convert_board_to_pieces_array(self.board)


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
