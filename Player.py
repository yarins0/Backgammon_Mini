from BoardTree import BoardTree
from Constants import *

class Player:
    def __init__(self, color, is_human=False):
        if color not in ["black", "white"]:
            raise ValueError("Color must be 'black' or 'white'.")
        self.color = color
        self.is_human = is_human
        self._pieces = [1, 1, 12, 12, 12, 12, 12, 17, 17, 17, 19, 19, 19, 19, 19] if color == "white" else [6, 6, 6, 6, 6, 8, 8, 8, 13, 13, 13, 13, 13, 24, 24]
        self.board_tree = None

    def play(self, board, roll):
        pass

    def is_human(self):
        pass

    def set_board_tree(self, board_tree):
        self.board_tree = board_tree

    def get_pieces(self):
        return self._pieces

    def set_other(self, other):
        self.other = other

    def get_other_pieces(self):
        return self.other.get_pieces()

    def set_pieces(self, list_of_pieces):
        self._pieces = list_of_pieces
        self.order()

    def order(self):
        self._pieces.sort()

    def win(self):
        return len(self._pieces) == 0

    def lose(self):
        return len(self.other._pieces) == 0

    def move_piece(self, distance, piece, r):
        if distance <= 0:
            raise ValueError('Distance must be greater than 0')

        if piece not in self._pieces:
            raise ValueError('The chosen piece is not valid')

        if self.captured_piece() and piece != (0 if self.color == "white" else 25):
            raise ValueError('You must move your captured piece first')

        target = piece + distance if self.color == "white" else piece - distance

        if not self.valid_move(piece, target, r):
            raise ValueError('That is an invalid place to move your piece')

        # Update the player's pieces
        self._pieces.remove(piece)
        if target != 0 and target != 25:
            self._pieces.append(target)
        self.order()

        # Handle capturing opponent's pieces
        self.capture_piece_at_position(target)

        # Update the board tree if using evaluation method 2
        if CHOSEN_EVAL_METHOD == 2:
            if not self.is_human():
                self.update_board_tree([piece, target])
            if self.other and not self.other.is_human():
                self.other.update_board_tree([piece, target])


    def capture_piece_at_position(self, position):
        if position in self.other._pieces:
            # Remove the opponent's piece from the board
            self.other._pieces.remove(position)
            # Place it on the bar (captured pieces)
            captured_position = 0 if self.other.color == "white" else 25
            self.other._pieces.append(captured_position)
            self.other.order()
            
    def captured_piece(self):
        return (0 if self.color == "white" else 25) in self._pieces

    def capture(self):
        op = self.get_other_pieces()[:]
        for piece in self._pieces:
            if piece in op:
                op[op.index(piece)] = 25 if self.color == "white" else 0
        self.other.set_pieces(op)

    def is_blocked(self, position: int) -> bool:
        # Determine if the position is blocked by two or more opponent pieces
        opponent_count = self.get_other_pieces().count(position)
        return opponent_count >= 2
    
    def valid_move(self, makor, yaad, r, board=None):
        if board is not None:
            return self.valid_move_with_board(makor, yaad, r, board)
        else:
            # Original valid_move logic without board
            if self.captured_piece() and makor != (0 if self.color == "white" else 25):
                return False

            if str(abs(yaad - makor)) in r and 1 <= yaad <= 24:
                return not self.is_blocked(yaad)

            if yaad >= 25 and self.color == "white":
                # Check if all pieces are in the home board (positions 19-24)
                if all(pos >= 19 for pos in self._pieces):
                    return True
                else:
                    return False

            if yaad <= 0 and self.color == "black":
                # Check if all pieces are in the home board (positions 1-6)
                if all(pos <= 6 for pos in self._pieces):
                    return True
                else:
                    return False

            return not self.is_blocked(yaad)
        
    def valid_move_with_board(self, makor, yaad, r, board):
        captured_position = 26 if self.color == "white" else 27
        home_positions = range(19, 25) if self.color == "white" else range(1, 7)

        # Check if any pieces are captured based on the board state
        if board[captured_position] > 0 and makor != (0 if self.color == "white" else 25):
            return False

        # Check if the move uses one of the die values
        if str(abs(yaad - makor)) not in r:
            return False

        # Determine if target position is within valid range
        if not (0 <= yaad <= 25):
            return False

        # Handle moving to a position
        if 1 <= yaad <= 24:
            return not self.is_blocked_on_board(yaad, board)

        # Handle bearing off
        if (self.color == "white" and yaad == 25) or (self.color == "black" and yaad == 0):
            # Collect all player's positions from the board
            player_positions = []
            for i in range(24):
                position = i + 1
                checker_count = board[i]
                if self.color == "white" and checker_count > 0:
                    player_positions.extend([position] * checker_count)
                elif self.color == "black" and checker_count < 0:
                    player_positions.extend([position] * abs(checker_count))
            # Check if all pieces are in home board
            if all(pos in home_positions for pos in player_positions):
                return True
        return False

    def is_blocked_on_board(self, position: int, board: list) -> bool:
        # Determine if the position is blocked by two or more opponent pieces on the given board
        opponent_count = -board[position-1] if self.color == "white" else board[position-1]
        return opponent_count >= 2


    def initialize_pieces_from_board(self, board: list):
        self._pieces = []
        for i, count in enumerate(board[:24]):
            position = i + 1
            if self.color == "white" and count > 0:
                self._pieces.extend([position] * count)
            elif self.color == "black" and count < 0:
                self._pieces.extend([position] * abs(count))

        # Add captured pieces from the bar
        captured_index = 26 if self.color == "white" else 27
        captured_count = board[captured_index]
        if captured_count > 0:
            self._pieces.extend([0 if self.color == "white" else 25] * captured_count)

        self.order()