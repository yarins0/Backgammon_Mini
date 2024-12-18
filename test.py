from AI_Player import AI_Player
from Human_Player import Human_Player

def test_ai_capture_opponent_piece():
    """
    Test the AI's ability to capture an opponent's piece, for both white and black.
    """
    print("Testing AI's ability to capture an opponent's piece:")
    
    for color in ['white', 'black']:
        # Set up the board state
        board = [0] * 28
        # Place AI's piece
        if color == 'white':
            ai_pos = 10
            opponent_pos = 15
            board[ai_pos] = 1
            board[opponent_pos] = -1  # Opponent's blot
        else:
            ai_pos = 13
            opponent_pos = 8
            board[ai_pos] = -1
            board[opponent_pos] = 1  # Opponent's blot

        # Create AI and opponent players
        ai_player = AI_Player(color, board)
        opponent_color = 'black' if color == 'white' else 'white'
        opponent_player = Human_Player(opponent_color, board)
        ai_player.set_other(opponent_player)
        opponent_player.set_other(ai_player)
        
        # AI's turn with a roll that allows capturing
        die_value = abs(opponent_pos - ai_pos)  # Calculate the die value needed
        roll = [die_value]
        
        # AI makes a move
        move_sequence = ai_player.play(roll.copy())
        # Execute the moves
        correct_move = False
        if move_sequence:
            for move in move_sequence:
                from_pos, to_pos = move
                if from_pos == ai_pos and to_pos == opponent_pos:
                    correct_move = True
                used_die_value = ai_player.move_piece(from_pos, to_pos, roll)
                roll.remove(used_die_value)
        
        # Print the result
        print(f"AI ({color}) attempted to capture opponent's piece from position {ai_pos} to {opponent_pos}.")
        if correct_move and board[opponent_player.get_captured_position()] > 0:
            print("Result: Success - AI captured the opponent's piece.")
        else:
            print("Result: Failure - AI did not capture the opponent's piece.")
        print(f"Board state after AI's move: {board}\n")
def test_ai_reenter_from_bar():
    """
    Test the AI's ability to re-enter from the bar, for both white and black.
    """
    print("Testing AI's ability to re-enter from the bar:")
    
    for color in ['white', 'black']:
        # Set up the board state
        board = [0] * 28
        # AI has one captured piece
        if color == 'white':
            opponent_blocks = {0: -2, 1: -2}
            entry_pos = 2
            board[24] = 1  # AI's bar (white)
        else:
            opponent_blocks = {23: 2, 22: 2}
            entry_pos = 21
            board[25] = 1  # AI's bar (black)
        
        # Set opponent's blocking pieces
        for pos, count in opponent_blocks.items():
            board[pos] = count
        
        # Create AI and opponent players
        ai_player = AI_Player(color, board)
        opponent_color = 'black' if color == 'white' else 'white'
        opponent_player = Human_Player(opponent_color, board)
        ai_player.set_other(opponent_player)
        opponent_player.set_other(ai_player)
        
        # Corrected die value calculation for re-entry
        if color == 'white':
            die_value = entry_pos + 1  # Positions 0-5 correspond to die values 1-6
        else:
            die_value = 24 - entry_pos  # Positions 23-18 correspond to die values 1-6
        
        roll = [die_value]

        # AI makes a move
        move_sequence = ai_player.play(roll.copy())
        # Execute the moves
        correct_move = False
        if move_sequence:
            for move in move_sequence:
                from_pos, to_pos = move
                if from_pos == ai_player.get_captured_position() and to_pos == entry_pos:
                    correct_move = True
                used_die_value = ai_player.move_piece(from_pos, to_pos, roll)
                if used_die_value in roll:
                    roll.remove(used_die_value)
        
        # Print the result
        print(f"AI ({color}) attempted to re-enter from bar to position {entry_pos}.")
        if correct_move and board[ai_player.get_captured_position()] == 0 and ai_player.is_piece_at_position(entry_pos, color):
            print("Result: Success - AI re-entered from the bar.")
        else:
            print("Result: Failure - AI did not re-enter correctly.")
        print(f"Board state after AI's move: {board}\n")

def test_ai_bear_off_pieces():
    """
    Test the AI's ability to bear off pieces, for both white and black, including from further positions.
    """
    print("Testing AI's ability to bear off pieces:")
    
    for color in ['white', 'black']:
        # Set up the board state
        board = [0] * 28
        # Place AI's pieces in home board positions
        if color == 'white':
            home_positions = {19: 2, 20: 3, 21: 3, 22: 3, 23: 4}
            escaped_position = 26
        else:
            home_positions = {5: -2, 4: -3, 3: -3, 2: -3, 1: -4}
            escaped_position = 27

        for pos, count in home_positions.items():
            board[pos] = count
        
        # Create AI and opponent players
        ai_player = AI_Player(color, board)
        opponent_color = 'black' if color == 'white' else 'white'
        opponent_player = Human_Player(opponent_color, board)
        ai_player.set_other(opponent_player)
        opponent_player.set_other(ai_player)
        
        # AI's turn with a roll that allows bearing off from further away
        roll = [6, 5]  # Use higher die values
        # AI makes a move
        move_sequence = ai_player.play(roll.copy())
        # Execute the moves
        correct_move = False
        borne_off_pieces_before = board[escaped_position]
        if move_sequence:
            for move in move_sequence:
                from_pos, to_pos = move
                if to_pos == escaped_position:
                    correct_move = True
                used_die_value = ai_player.move_piece(from_pos, to_pos, roll)
                roll.remove(used_die_value)
        
        # Check if pieces were borne off
        borne_off_pieces_after = board[escaped_position]
        # Print the result
        print(f"AI ({color}) attempted to bear off pieces.")
        if correct_move and borne_off_pieces_after > borne_off_pieces_before:
            print("Result: Success - AI bore off pieces.")
        else:
            print("Result: Failure - AI did not bear off any pieces.")
        print(f"Board state after AI's move: {board}\n")

if __name__ == "__main__":
    test_ai_capture_opponent_piece()
    test_ai_reenter_from_bar()
    test_ai_bear_off_pieces()