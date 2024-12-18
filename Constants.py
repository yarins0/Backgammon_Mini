MIN_MAX_DEPTH = 2  # Default depth for min-max search
CHOSEN_EVAL_METHOD = 2 # Choose 1 for heuristic, 2 for strategic (min max)

CONSIDER_DICE_PROBABILITIES = False
EVAL_DISTRIBUTION = {
    "prime_structure": 0.2,
    "anchors": 0.1,
    "blots": 0.1,
    "race_advantage": 0.3,  # Adjusted from 0.4 to accommodate the new factor
    "home_board_strength": 0.1,
    "captured_pieces": 0.2,  # New evaluation factor
}

TURN_TIME = 1000  # Default turn time limit in seconds
AI_DELAY = 20  # Delay between AI moves in milliseconds

DEBUG_MODE = True
SAFE_TEST = False # Set to True to test AI without initializing pieces from board