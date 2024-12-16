import unittest
from AI_Player import AI_Player
from Player import Player
from Constants import EVAL_DISTRIBUTION, CHOSEN_EVAL_METHOD, MIN_MAX_DEPTH, SAFE_TEST


class TestAIPlayerEdgeCases(unittest.TestCase):
    def setUp(self):
        # Set up players
        self.white_ai = AI_Player("white", ratios=EVAL_DISTRIBUTION)
        self.black_ai = AI_Player("black", ratios=EVAL_DISTRIBUTION)
        self.white_ai.set_other(self.black_ai)
        self.black_ai.set_other(self.white_ai)

    def test_ai_with_captured_pieces(self):
        # Board setup: White has 2 captured pieces
        board = [0] * 28
        board[26] = 2  # White's captured pieces
        board[0] = -2  # Black occupies point 1
        board[1] = -2  # Black occupies point 2
        board[2] = -2  # Black occupies point 3
        board[3] = -2  # Black occupies point 4
        board[4] = -2  # Black occupies point 5
        board[5] = -2  # Black occupies point 6
        roll = [1, 2]
        self.white_ai.initialize_pieces_from_board(board)
        move_sequence = self.white_ai.play(board, roll)
        # AI should have no valid moves
        self.assertEqual(move_sequence, [], "AI should not have any valid moves when entry points are blocked.")

    def test_ai_bearing_off(self):
        # Board setup: White has all pieces in home board
        board = [0] * 28
        # Positions 19-24
        board[18] = 2
        board[19] = 3
        board[20] = 4
        board[21] = 2
        board[22] = 2
        board[23] = 2
        roll = [6, 1]
        self.white_ai.initialize_pieces_from_board(board)
        move_sequence = self.white_ai.play(board, roll)
        # AI should bear off pieces
        self.assertTrue(any(move[1] == 25 for move in move_sequence), "AI did not bear off pieces as expected.")

    def test_ai_with_no_valid_moves(self):
        # Board setup: White has no valid moves
        board = [0] * 28
        board[26] = 2  # White's captured pieces
        # Black occupies points 1-6
        for i in range(6):
            board[i] = -2
        roll = [1, 2]
        self.white_ai.initialize_pieces_from_board(board)
        move_sequence = self.white_ai.play(board, roll)
        # AI should have no valid moves
        self.assertEqual(move_sequence, [], "AI should not have any valid moves.")

    def test_ai_rolling_doubles(self):
        # Board setup: White has pieces on point 6
        board = [0] * 28
        board[5] = 5  # Point 6
        roll = [3, 3, 3 ,3]  # Double 3
        self.white_ai.initialize_pieces_from_board(board)
        move_sequence = self.white_ai.play(board, roll)
        # AI should use all four moves
        self.assertEqual(len(move_sequence), 4, "AI should make four moves when rolling doubles.")

    def test_ai_attempts_valid_moves_only(self):
        # Board setup: AI should not attempt invalid moves
        board = [0] * 28
        board[5] = 1  # White piece on point 6
        board[6] = -2  # Black blocks point 7
        roll = [1, 2]
        self.white_ai.initialize_pieces_from_board(board)
        move_sequence = self.white_ai.play(board, roll)
        # AI should not move to blocked point 7
        invalid_moves = [move for move in move_sequence if move[1] == 7]
        self.assertEqual(invalid_moves, [], "AI should not attempt to move to blocked point 7.")

    def test_ai_executes_winning_move(self):
        # Board setup: White has one piece left to bear off
        board = [0] * 28
        board[23] = 1  # White piece on point 24
        board[24] = 14  # White has 14 pieces borne off
        roll = [1, 2]
        self.white_ai.initialize_pieces_from_board(board)
        move_sequence = self.white_ai.play(board, roll)
        # AI should bear off last piece
        self.assertTrue(any(move[1] == 25 for move in move_sequence), "AI should bear off the last piece and win.")
        # Simulate the move
        for move in move_sequence:
            board = self.white_ai.simulate_move(board, move)
        self.white_ai.initialize_pieces_from_board(board)
        # AI should recognize the win
        self.assertTrue(self.white_ai.win(), "AI should recognize a winning condition.")

    def test_ai_does_not_move_opponent_pieces(self):
        # Board setup: AI should not move opponent's pieces
        board = [0] * 28
        board[5] = 1  # White piece on point 6
        board[6] = -1  # Black piece on point 7
        roll = [1, 6]
        self.white_ai.initialize_pieces_from_board(board)
        move_sequence = self.white_ai.play(board, roll)
        # Ensure AI does not attempt to move from positions it doesn't own
        for move in move_sequence:
            self.assertIn(move[0], self.white_ai._pieces + [0], "AI attempted to move a piece not belonging to it.")

if __name__ == '__main__':
    unittest.main()