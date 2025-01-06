MIN_MAX_DEPTH = 1  # Default depth for min-max search
CHOSEN_EVAL_METHOD = 2 # Choose 1 for heuristic, 2 for MCTS, 3 for strategic (min max)

WHITE = "white"
BLACK = "black"
START_BOARD = [2, 0, 0, 0, 0, -5, 0, -3, 0, 0, 0, 5, -5, 0, 0, 0, 3, 0, 5, 0, 0, 0, 0, -2, 0, 0, 0, 0]

MCTS_C = 1.4 # Exploration parameter for UCB
TURN_TIME = 60  # Default turn time limit in seconds
AI_TURN_TIME = 5  # Default AI turn time limit in seconds
AI_DELAY = 0  # Delay between AI moves in milliseconds

CONSIDER_DICE_PROBABILITIES = False
EVAL_DISTRIBUTION = {
    "prime_structure": 1,
    "anchors": 0,
    "blots": 0,
    "race_advantage": 0,
    "home_board_strength": 0,
    "captured_pieces": 0,
}

DEBUG_MODE = True
SAFE_TEST = False # Set to True to test AI without initializing pieces from board