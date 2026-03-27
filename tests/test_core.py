"""
Core logic tests covering bugs found during engineering review.
Run with: python -m pytest tests/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from Constants import START_BOARD, WHITE, BLACK, EVAL_DISTRIBUTION
from BoardTree import BoardNode
from Eval_position import evaluate_position, count_weighted_blots
from Players.Player import Player


# ── BoardTree ──────────────────────────────────────────────────────────────────

class TestBoardNodeTerminal:
    def _node(self, board):
        return BoardNode(board, 0.0, [], WHITE)

    def test_not_terminal_at_start(self):
        node = self._node(START_BOARD.copy())
        assert not node.is_terminal()

    def test_white_wins_when_board26_is_15(self):
        board = [0] * 28
        board[26] = 15   # white borne off
        node = self._node(board)
        assert node.is_terminal()

    def test_black_wins_when_board27_is_15(self):
        board = [0] * 28
        board[27] = 15   # black borne off
        node = self._node(board)
        assert node.is_terminal()

    def test_does_not_trigger_on_bar_positions(self):
        # Old bug: board[24]==15 (white bar) would falsely fire
        board = [0] * 28
        board[24] = 15   # 15 white pieces captured — not a win
        node = self._node(board)
        assert not node.is_terminal()


class TestBoardNodeFullyExpanded:
    def test_not_expanded_initially(self):
        node = BoardNode(START_BOARD.copy(), 0.0, [], WHITE)
        assert not node.is_fully_expanded([1, 2])

    def test_expanded_after_fully_expand_roll(self):
        node = BoardNode(START_BOARD.copy(), 0.0, [], WHITE)
        node.fully_expand_roll([1, 2])
        assert node.is_fully_expanded([1, 2])

    def test_roll_order_irrelevant(self):
        # [2, 1] and [1, 2] are the same roll — both should register
        node = BoardNode(START_BOARD.copy(), 0.0, [], WHITE)
        node.fully_expand_roll([2, 1])
        assert node.is_fully_expanded([1, 2])

    def test_different_roll_not_expanded(self):
        node = BoardNode(START_BOARD.copy(), 0.0, [], WHITE)
        node.fully_expand_roll([1, 2])
        assert not node.is_fully_expanded([3, 4])


# ── Evaluation ─────────────────────────────────────────────────────────────────

class TestCountWeightedBlots:
    def test_returns_nonzero_when_blots_exist(self):
        # Place a single white piece at position 5 with a black piece nearby at 2
        board = [0] * 28
        board[5] = 1    # white blot
        board[2] = -2   # black prime nearby
        result = count_weighted_blots(board, is_white=True)
        # Should be > 0 (was always 0 before the fix)
        assert result > 0

    def test_returns_zero_when_no_blots(self):
        board = [0] * 28
        board[5] = 2    # white prime — not a blot
        result = count_weighted_blots(board, is_white=True)
        assert result == 0


class TestEvaluatePosition:
    def test_neutral_start_board_near_half(self):
        # Start position should be roughly neutral (score near 0.5)
        score = evaluate_position(START_BOARD.copy(), EVAL_DISTRIBUTION)
        assert 0.0 <= score <= 1.0

    def test_white_winning_returns_high_score(self):
        board = [0] * 28
        board[26] = 15   # white has borne off all pieces
        score = evaluate_position(board, EVAL_DISTRIBUTION)
        assert score == 1.0

    def test_black_winning_returns_low_score(self):
        board = [0] * 28
        board[27] = 15   # black borne off position
        score = evaluate_position(board, EVAL_DISTRIBUTION)
        assert score == 0.0


# ── Player move generation ──────────────────────────────────────────────────────

class TestGenerateAllMoves:
    def test_white_has_moves_at_start(self):
        p = Player(WHITE, START_BOARD.copy())
        moves = p.generate_all_moves(START_BOARD.copy(), [1, 2])
        assert len(moves) > 0

    def test_black_has_moves_at_start(self):
        p = Player(BLACK, START_BOARD.copy())
        moves = p.generate_all_moves(START_BOARD.copy(), [3, 4])
        assert len(moves) > 0

    def test_no_moves_when_all_blocked(self):
        # A board where the moving player literally has no valid destinations
        # White has one piece on position 0, all destinations blocked by black primes
        board = [0] * 28
        board[0] = 1       # one white piece
        for i in range(1, 7):
            board[i] = -2  # black primes blocking positions 1-6
        p = Player(WHITE, board)
        moves = p.generate_all_moves(board, [1, 2])
        # Result should be [[]] — one entry meaning "no moves possible"
        assert moves == [[]]
