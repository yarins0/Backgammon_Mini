
from Constants import *


def evaluate_position(board, ratios=EVAL_DISTRIBUTION):
    """
    Evaluates the current board position for the white player using custom ratios.
    
    :param board: The current board state.
    :param ratios: A dictionary containing the evaluation ratios.
    :return: The evaluated score of the board.
    """
    
    # Validate the ratios dictionary
    if len(ratios) != 5:
        raise ValueError("Ratios dictionary must contain exactly 5 elements.")
    if not abs(sum(ratios.values()) - 1.0) < 1e-6:
        raise ValueError("The sum of the ratios must be 1.")

    prime_structure = evaluate_prime_structure(board)
    anchors = evaluate_anchors(board)
    blots = evaluate_blots(board, consider_dice_probabilities=True)
    race_advantage = evaluate_race_advantage(board)
    home_board_strength = evaluate_home_board_strength(board)

    # Check if all pieces have passed each other
    if all_pieces_have_passed_each_other(board):
        return race_advantage
    
    # Add a winning condition bonus
    winning_bonus = 0
    if all_pieces_in_home(board, is_white=True):
        winning_bonus = 1.0  # Adjust this value to heavily reward winning positions


    return (prime_structure * ratios.get("prime_structure") +
            anchors * ratios.get("anchors") +
            blots * ratios.get("blots") +
            race_advantage * ratios.get("race_advantage") +
            home_board_strength * ratios.get("home_board_strength") +
            winning_bonus)

def all_pieces_have_passed_each_other(board):
    """
    Check if all black pieces appear before all white pieces in the board array from cells 0-23.
    
    :param board: The current board state.
    :return: True if all black pieces appear before all white pieces, False otherwise.
    """
    # Iterate over the board from cells 0-23
    passed_black = False
    for position in range(24):
        if board[position] < 0:
            if passed_black:
                # If we encounter a black piece after a white piece, return False
                return False
        elif board[position] > 0:
            # Mark that we've passed a white piece
            passed_black = True

    return True

def all_pieces_in_home(board, is_white):
    # Check if all pieces are in the home board
    home_range = range(19, 25) if is_white else range(1, 7)
    return all(board[pos] > 1 for pos in home_range)
                           

def evaluate_prime_structure(board):
    # Counts the number of 4+ consecutive occupied points for both players and evaluates comparatively.
    white_primes = count_primes(board, is_white=True)
    black_primes = count_primes(board, is_white=False)
    return normalize(white_primes, black_primes)

def evaluate_anchors(board):
    # Counts the number of points occupied in the opponent's home board for both players.
    white_anchors = count_anchors(board, is_white=True)
    black_anchors = count_anchors(board, is_white=False)
    return normalize(white_anchors, black_anchors)

def evaluate_blots(board, consider_dice_probabilities=False):
    # Counts single checkers on any point for each player and prefers fewer for the current player.
    # If consider_dice_probabilities is True, weights penalties based on opponent's likelihood to hit.
    penalty_factor = 1.5  # Increase this factor to penalize blots more
    if consider_dice_probabilities:
        white_blots = count_weighted_blots(board, is_white=True) * penalty_factor
        black_blots = count_weighted_blots(board, is_white=False) * penalty_factor
    else:
        white_blots = count_simple_blots(board, is_white=True) * penalty_factor
        black_blots = count_simple_blots(board, is_white=False) * penalty_factor
    return normalize(black_blots, white_blots)  # Opponent's blots are advantageous

def evaluate_race_advantage(board):
    # Computes the total distance (pip count) to bear off all checkers for both players.
    white_pip_count = calculate_pip_count(board, is_white=True)
    black_pip_count = calculate_pip_count(board, is_white=False)
    return normalize(black_pip_count, white_pip_count)  # Lower pip count is better

def evaluate_home_board_strength(board):
    # Counts how many points are “made” (2+ checkers) in the home board.
    white_strength = count_home_board_points(board, is_white=True)
    black_strength = count_home_board_points(board, is_white=False)
    return normalize(white_strength, black_strength)

def normalize(black_value, white_value):
    if black_value + white_value == 0:
        return 0.5  # Neutral position
    return white_value / (white_value + black_value)

def count_primes(board, is_white):
    direction = 1 if is_white else -1
    primes = 0
    current_prime_length = 0
    for point in range(0, 24):
        if board[point] * direction > 1:
            current_prime_length += 1
            if current_prime_length >= 4:
                primes += 1
        else:
            current_prime_length = 0
    return primes

def count_anchors(board, is_white):
    direction = 1 if is_white else -1
    start, end = (0, 6) if is_white else (18, 24)
    anchors = sum(1 for point in range(start, end) if board[point] * direction > 0)
    return anchors

def count_simple_blots(board, is_white):
    direction = 1 if is_white else -1
    return sum(1 for point in range(24) if board[point] * direction == 1)

def count_weighted_blots(board, is_white):
    from collections import Counter
    direction = 1 if is_white else -1
    blots = [point for point in range(24) if board[point] * direction == 1]
    opponent_points = [i for i, x in enumerate(board[:24]) if x * direction < 0]

    weighted_blots = 0
    for blot in blots:
        min_distance = min(abs(blot - opp) for opp in opponent_points) if opponent_points else float('inf')
        hit_probability = calculate_hit_probability(min_distance)
        weighted_blots *= hit_probability
    return weighted_blots

def calculate_hit_probability(distance):
    # Using a hash map to store all possible distances and their probabilities
    dice_probabilities = {
        1: 11 / 36,  # Rolling 1 or 1 from combinations
        2: 10 / 36,
        3: 9 / 36,
        4: 8 / 36,
        5: 7 / 36,
        6: 6 / 36,
        7: 5 / 36,
        8: 4 / 36,
        9: 3 / 36,
        10: 2 / 36,
        11: 1 / 36,
        12: 1 / 36,
    }

    if distance in dice_probabilities:
        return dice_probabilities[distance]
    return 0

def calculate_pip_count(board, is_white):
    direction = 1 if is_white else -1
    pip_count = 0
    for point in range(24):
        if board[point] * direction > 0:
            pip_count += (25 - point if is_white else point + 1) * abs(board[point])
    captured_pieces = board[26] if is_white else board[27]
    pip_count += captured_pieces * 25
    return pip_count

def count_home_board_points(board, is_white):
    direction = 1 if is_white else -1
    start, end = (18, 24) if is_white else (0, 6)
    return sum(1 for point in range(start, end) if board[point] * direction >= 2)

