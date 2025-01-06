MIN_MAX_DEPTH = 1  # Default depth for min-max search
CHOSEN_EVAL_METHOD = 2 # Choose 1 for heuristic, 2 for strategic (min max)

CONSIDER_DICE_PROBABILITIES = False
EVAL_DISTRIBUTION = {
    "prime_structure": 1,
    "anchors": 0,
    "blots": 0,
    "race_advantage": 0,
    "home_board_strength": 0,
    "captured_pieces": 0,
}

TURN_TIME = 60  # Default turn time limit in seconds
AI_DELAY = 0  # Delay between AI moves in milliseconds

DEBUG_MODE = True
SAFE_TEST = False # Set to True to test AI without initializing pieces from board